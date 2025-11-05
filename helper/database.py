import motor.motor_asyncio
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

# --- Reverted to the simple verification structure ---
default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'file_payload': ""
}

class MongoDB:
    _instances = {}

    def __new__(cls, uri: str, db_name: str, logger):
        if (uri, db_name) not in cls._instances:
            instance = super().__new__(cls)
            instance.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            instance.db = instance.client[db_name]
            instance.user_data = instance.db["users"]
            instance.paid_data = instance.db["paid_users"]  # Changed from pros to paid_users
            instance.channel_data = instance.db["channels"]
            instance.settings_collection = instance.db['bot_settings']
            instance.stats_collection = instance.db['daily_stats']
            instance.verify_counts = instance.db["daily_verify_counts"]
            instance.payment_logs = instance.db["payment_logs"]  # New collection for payment tracking
            instance.LOGGER = logger
            cls._instances[(uri, db_name)] = instance
        return cls._instances[(uri, db_name)]

    async def get_verify_status(self, user_id: int):
        user = await self.user_data.find_one({'_id': user_id})
        return user.get('verify_status', default_verify) if user else default_verify

    async def update_verify_status(self, user_id: int, status: dict):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'verify_status': status}}, upsert=True)

    async def reset_all_verify_counts(self):
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        await self.verify_counts.delete_many({'_id': {'$lt': today_str}})

    async def increment_verify_count(self):
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        await self.verify_counts.update_one({'_id': today_str}, {'$inc': {'count': 1}}, upsert=True)

    async def get_verify_stats(self):
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        today_data = await self.verify_counts.find_one({'_id': today_str})
        yesterday_data = await self.verify_counts.find_one({'_id': yesterday_str})
        today_count = today_data.get('count', 0) if today_data else 0
        yesterday_count = yesterday_data.get('count', 0) if yesterday_data else 0
        return today_count, yesterday_count

    # --- Updated for paid user system ---
    async def get_user_state(self, user_id: int):
        try:
            user_doc = await self.user_data.find_one({'_id': user_id}, {'ban': 1})
            paid_doc = await self.paid_data.find_one({'_id': user_id})
            
            if not user_doc:
                await self.add_user(user_id)
                user_doc = {}
            
            is_paid = False
            expires_at = None
            plan_name = "𝖥𝗋𝖾𝖾"
            
            if paid_doc:
                expires_at = paid_doc.get('expires_at')
                is_paid = True
                plan_name = paid_doc.get('plan_name', '𝖯𝗋𝖾𝗆𝗂𝗎𝗆')
                
                if expires_at:
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) > expires_at:
                        is_paid = False
                        # 𝖠𝗎𝗍𝗈-𝖼𝗅𝖾𝖺𝗇 𝗎𝗉 𝖾𝗑𝗉𝗂𝗋𝖾𝖽 𝗎𝗌𝖾𝗋𝗌
                        await self.remove_paid_user(user_id)

            state = {
                'banned': user_doc.get('ban', False),
                'is_paid': is_paid,
                'plan_name': plan_name
            }
            return state, expires_at
        except Exception as e:
            self.LOGGER(__name__, "DB_STATE").error(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝗀𝖾𝗍 𝗎𝗌𝖾𝗋 𝗌𝗍𝖺𝗍𝖾 𝖿𝗈𝗋 {user_id}: {e}", exc_info=True)
            return None, None

    async def cleanup_expired_paid_users(self):
        """𝖢𝗅𝖾𝖺𝗇 𝗎𝗉 𝖾𝗑𝗉𝗂𝗋𝖾𝖽 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋𝗌"""
        expired_user_ids = []
        try:
            now_utc = datetime.now(timezone.utc)
            expired_users_cursor = self.paid_data.find({'expires_at': {'$ne': None, '$lt': now_utc}})
            async for user_doc in expired_users_cursor:
                user_id = user_doc['_id']
                expired_user_ids.append(user_id)
                await self.remove_paid_user(user_id)
                
                # 𝖭𝗈𝗍𝗂𝖿𝗒 𝗎𝗌𝖾𝗋 𝖺𝖻𝗈𝗎𝗍 𝖾𝗑𝗉𝗂𝗋𝖺𝗍𝗂𝗈𝗇 (𝗈𝗉𝗍𝗂𝗈𝗇𝖺𝗅)
                try:
                    # 𝖸𝗈𝗎 𝖼𝖺𝗇 𝖺𝖽𝖽 𝗇𝗈𝗍𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝗅𝗈𝗀𝗂𝖼 𝗁𝖾𝗋𝖾
                    pass
                except Exception:
                    pass
                    
            if expired_user_ids:
                self.LOGGER(__name__, "DB_CLEANUP").info(f"𝖢𝗅𝖾𝖺𝗇𝖾𝖽 𝗎𝗉 {len(expired_user_ids)} 𝖾𝗑𝗉𝗂𝗋𝖾𝖽 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋𝗌.")
            return expired_user_ids
        except Exception as e:
            self.LOGGER(__name__, "DB_CLEANUP").error(f"𝖤𝗋𝗋𝗈𝗋 𝖽𝗎𝗋𝗂𝗇𝗀 𝖾𝗑𝗉𝗂𝗋𝖾𝖽 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋 𝖼𝗅𝖾𝖺𝗇𝗎𝗉: {e}", exc_info=True)
            return []

    async def add_user(self, user_id: int, ban_status: bool = False):
        try:
            await self.user_data.update_one(
                {'_id': user_id}, 
                {'$set': {'ban': ban_status}}, 
                upsert=True
            )
        except Exception as e:
            self.LOGGER(__name__, "DB_USER").error(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖺𝖽𝖽/𝗎𝗉𝖽𝖺𝗍𝖾 𝗎𝗌𝖾𝗋 {user_id}: {e}")

    async def present_user(self, user_id: int):
        return await self.user_data.find_one({'_id': user_id}) is not None

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})

    async def full_userbase(self):
        return [doc['_id'] async for doc in self.user_data.find({}, {'_id': 1})]

    async def is_user_in_channel(self, channel_id: int, user_id: int):
        return await self.channel_data.find_one({"_id": channel_id, "users": user_id}) is not None

    # --- Updated paid user methods ---
    async def is_paid_user(self, user_id: int):
        """𝖢𝗁𝖾𝖼𝗄 𝗂𝖿 𝗎𝗌𝖾𝗋 𝗂𝗌 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋"""
        state, _ = await self.get_user_state(user_id)
        return state.get('is_paid', False) if state else False

    async def is_banned(self, user_id: int):
        state, _ = await self.get_user_state(user_id)
        return state.get('banned', False) if state else False

    async def get_paid_user(self, user_id: int):
        """𝖦𝖾𝗍 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋 𝖽𝖾𝗍𝖺𝗂𝗅𝗌"""
        return await self.paid_data.find_one({'_id': user_id})

    async def add_paid_user(self, user_id: int, plan_name: str, price: str, expires_at=None, added_by: int = None):
        """𝖠𝖽𝖽 𝖺 𝗇𝖾𝗐 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋"""
        try:
            paid_data = {
                '_id': user_id,
                'plan_name': plan_name,
                'price': price,
                'expires_at': expires_at,
                'added_at': datetime.now(timezone.utc),
                'added_by': added_by,
                'is_permanent': expires_at is None
            }
            
            await self.paid_data.update_one(
                {'_id': user_id}, 
                {'$set': paid_data}, 
                upsert=True
            )
            
            # 𝖫𝗈𝗀 𝗍𝗁𝖾 𝗉𝖺𝗒𝗆𝖾𝗇𝗍
            await self.log_payment(user_id, plan_name, price, added_by)
            
            return True
        except Exception as e:
            self.LOGGER(__name__, "DB_PAID").error(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖺𝖽𝖽 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋 {user_id}: {e}")
            return False

    async def remove_paid_user(self, user_id: int):
        """𝖱𝖾𝗆𝗈𝗏𝖾 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋"""
        try:
            result = await self.paid_data.delete_one({'_id': user_id})
            return result.deleted_count > 0
        except Exception as e:
            self.LOGGER(__name__, "DB_PAID").error(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝗋𝖾𝗆𝗈𝗏𝖾 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋 {user_id}: {e}")
            return False

    async def get_paid_users_list(self):
        """𝖦𝖾𝗍 𝖺𝗅𝗅 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋𝗌"""
        return [doc async for doc in self.paid_data.find()]

    async def get_active_paid_users_count(self):
        """𝖦𝖾𝗍 𝖼𝗈𝗎𝗇𝗍 𝗈𝖿 𝖺𝖼𝗍𝗂𝗏𝖾 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋𝗌"""
        try:
            now_utc = datetime.now(timezone.utc)
            # 𝖢𝗈𝗎𝗇𝗍 𝗉𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍 𝗎𝗌𝖾𝗋𝗌 𝖺𝗇𝖽 𝗇𝗈𝗇-𝖾𝗑𝗉𝗂𝗋𝖾𝖽 𝗍𝖾𝗆𝗉𝗈𝗋𝖺𝗋𝗒 𝗎𝗌𝖾𝗋𝗌
            count = await self.paid_data.count_documents({
                '$or': [
                    {'expires_at': None},
                    {'expires_at': {'$gt': now_utc}}
                ]
            })
            return count
        except Exception as e:
            self.LOGGER(__name__, "DB_PAID").error(f"𝖤𝗋𝗋𝗈𝗋 𝖼𝗈𝗎𝗇𝗍𝗂𝗇𝗀 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋𝗌: {e}")
            return 0

    async def log_payment(self, user_id: int, plan_name: str, price: str, added_by: int = None):
        """𝖫𝗈𝗀 𝗉𝖺𝗒𝗆𝖾𝗇𝗍 𝖿𝗈𝗋 𝗍𝗋𝖺𝖼𝗄𝗂𝗇𝗀"""
        try:
            payment_log = {
                'user_id': user_id,
                'plan_name': plan_name,
                'price': price,
                'added_by': added_by,
                'timestamp': datetime.now(timezone.utc)
            }
            await self.payment_logs.insert_one(payment_log)
        except Exception as e:
            self.LOGGER(__name__, "DB_PAYMENT_LOG").error(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝗅𝗈𝗀 𝗉𝖺𝗒𝗆𝖾𝗇𝗍: {e}")

    async def get_payment_stats(self, days: int = 30):
        """𝖦𝖾𝗍 𝗉𝖺𝗒𝗆𝖾𝗇𝗍 𝗌𝗍𝖺𝗍𝗌 𝗈𝗏𝖾𝗋 𝗍𝗁𝖾 𝗅𝖺𝗌𝗍 𝖭 𝖽𝖺𝗒𝗌"""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # 𝖳𝗈𝗍𝖺𝗅 𝗉𝖺𝗒𝗆𝖾𝗇𝗍𝗌
            total_payments = await self.payment_logs.count_documents({
                'timestamp': {'$gte': start_date}
            })
            
            # 𝖳𝗈𝗍𝖺𝗅 𝗋𝖾𝗏𝖾𝗇𝗎𝖾
            pipeline = [
                {'$match': {'timestamp': {'$gte': start_date}}},
                {'$group': {'_id': None, 'total_revenue': {'$sum': {'$toDouble': '$price'}}}}
            ]
            revenue_result = await self.payment_logs.aggregate(pipeline).to_list(length=1)
            total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
            
            return total_payments, total_revenue
        except Exception as e:
            self.LOGGER(__name__, "DB_STATS").error(f"𝖤𝗋𝗋𝗈𝗋 𝗀𝖾𝗍𝗍𝗂𝗇𝗀 𝗉𝖺𝗒𝗆𝖾𝗇𝗍 𝗌𝗍𝖺𝗍𝗌: {e}")
            return 0, 0

    # --- Legacy methods for backward compatibility ---
    async def is_pro(self, user_id: int):
        """𝖫𝖾𝗀𝖺𝖼𝗒 𝗆𝖾𝗍𝗁𝗈𝖽 - 𝖺𝗅𝗂𝖺𝗌 𝖿𝗈𝗋 𝗂𝗌_𝗉𝖺𝗂𝖽_𝗎𝗌𝖾𝗋"""
        return await self.is_paid_user(user_id)

    async def get_pro_user(self, user_id: int):
        """𝖫𝖾𝗀𝖺𝖼𝗒 𝗆𝖾𝗍𝗁𝗈𝖽 - 𝖺𝗅𝗂𝖺𝗌 𝖿𝗈𝗋 𝗀𝖾𝗍_𝗉𝖺𝗂𝖽_𝗎𝗌𝖾𝗋"""
        return await self.get_paid_user(user_id)

    async def add_pro(self, user_id, expires_at=None):
        """𝖫𝖾𝗀𝖺𝖼𝗒 𝗆𝖾𝗍𝗁𝗈𝖽"""
        return await self.add_paid_user(user_id, "𝖫𝖾𝗀𝖺𝖼𝗒 𝖯𝗅𝖺𝗇", "𝖭/𝖠", expires_at)

    async def remove_pro(self, user_id: int):
        """𝖫𝖾𝗀𝖺𝖼𝗒 𝗆𝖾𝗍𝗁𝗈𝖽"""
        return await self.remove_paid_user(user_id)

    async def get_pros_list(self):
        """𝖫𝖾𝗀𝖺𝖼𝗒 𝗆𝖾𝗍𝗁𝗈𝖽"""
        return await self.get_paid_users_list()

    # --- Existing methods remain unchanged ---
    async def increment_shortener_clicks(self):
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        await self.stats_collection.update_one({'_id': today_str}, {'$inc': {'clicks': 1}}, upsert=True)

    async def get_stats(self):
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        today_data = await self.stats_collection.find_one({'_id': today_str})
        yesterday_data = await self.stats_collection.find_one({'_id': yesterday_str})
        today_clicks = today_data.get('clicks', 0) if today_data else 0
        yesterday_clicks = yesterday_data.get('clicks', 0) if yesterday_data else 0
        return today_clicks, yesterday_clicks

    async def load_settings(self, session_name: str):
        return await self.settings_collection.find_one({'_id': session_name})

    async def save_settings(self, session_name: str, settings: dict):
        await self.settings_collection.update_one({'_id': session_name}, {'$set': settings}, upsert=True)

    async def set_channels(self, channels: list[int]):
        await self.user_data.update_one({"_id": 1}, {"$set": {"channels": channels}}, upsert=True)

    async def add_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one({"_id": channel_id}, {"$addToSet": {"users": user_id}}, upsert=True)

    async def ban_user(self, user_id: int):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'ban': True}}, upsert=True)

    async def unban_user(self, user_id: int):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'ban': False}}, upsert=True)
