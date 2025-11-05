from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta, timezone
from pyrogram.errors import PeerIdInvalid, UserIsBlocked, InputUserDeactivated
from zoneinfo import ZoneInfo
import asyncio

from bot import Bot
import config

# Define the Indian Standard Time zone
IST = ZoneInfo("Asia/Kolkata")

#========================================================================#

class PaidUserManager:
    def __init__(self, client: Bot):
        self.client = client
        self.payment_plans = {
            '1d': {'duration': timedelta(days=1), 'price': '₹50', 'name': '1 𝖣𝖺𝗒'},
            '7d': {'duration': timedelta(days=7), 'price': '₹250', 'name': '1 𝖶𝖾𝖾𝗄'},
            '1m': {'duration': timedelta(days=30), 'price': '₹800', 'name': '1 𝖬𝗈𝗇𝗍𝗁'},
            '3m': {'duration': timedelta(days=90), 'price': '₹2000', 'name': '3 𝖬𝗈𝗇𝗍𝗁𝗌'},
            '1y': {'duration': timedelta(days=365), 'price': '₹5000', 'name': '1 𝖸𝖾𝖺𝗋'},
            'perm': {'duration': None, 'price': '₹15000', 'name': '𝖯𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍'}
        }
    
    def parse_custom_duration(self, amount: int, unit: str) -> timedelta:
        """𝖯𝖺𝗋𝗌𝖾 𝖼𝗎𝗌𝗍𝗈𝗆 𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝖿𝗈𝗋 𝗆𝖺𝗇𝗎𝖺𝗅 𝖺𝗎𝗍𝗁𝗈𝗋𝗂𝗓𝖺𝗍𝗂𝗈𝗇"""
        unit_map = {
            's': timedelta(seconds=amount),
            'm': timedelta(minutes=amount),
            'h': timedelta(hours=amount),
            'd': timedelta(days=amount),
            'w': timedelta(weeks=amount),
            'y': timedelta(days=amount * 365)
        }
        return unit_map.get(unit.lower())

    async def validate_user(self, user_id: int) -> dict:
        """𝖵𝖺𝗅𝗂𝖽𝖺𝗍𝖾 𝗂𝖿 𝗎𝗌𝖾𝗋 𝖾𝗑𝗂𝗌𝗍𝗌 𝖺𝗇𝖽 𝖼𝖺𝗇 𝖻𝖾 𝖼𝗈𝗇𝗍𝖺𝖼𝗍𝖾𝖽"""
        try:
            user = await self.client.get_users(user_id)
            return {
                'exists': True,
                'user': user,
                'name': user.first_name + (" " + user.last_name if user.last_name else ""),
                'username': f"@{user.username}" if user.username else "𝖭𝗈 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾"
            }
        except PeerIdInvalid:
            return {'exists': False, 'error': '𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗎𝗌𝖾𝗋 𝖨𝖣'}
        except Exception as e:
            return {'exists': False, 'error': str(e)}

    def format_expiry_display(self, expires_at: datetime, is_permanent: bool) -> str:
        """𝖥𝗈𝗋𝗆𝖺𝗍 𝖾𝗑𝗉𝗂𝗋𝗒 𝖿𝗈𝗋 𝖽𝗂𝗌𝗉𝗅𝖺𝗒 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌"""
        if is_permanent:
            return "**𝖯𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍 𝖠𝖼𝖼𝖾𝗌𝗌** ♾️"
        
        expires_ist = expires_at.astimezone(IST)
        time_remaining = expires_ist - datetime.now(IST)
        
        # 𝖥𝗈𝗋𝗆𝖺𝗍 𝗍𝗂𝗆𝖾 𝗋𝖾𝗆𝖺𝗂𝗇𝗂𝗇𝗀
        days = time_remaining.days
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes = remainder // 60
        
        time_parts = []
        if days > 0:
            time_parts.append(f"{days} 𝖽𝖺𝗒{'𝗌' if days != 1 else ''}")
        if hours > 0:
            time_parts.append(f"{hours} 𝗁𝗈𝗎𝗋{'𝗌' if hours != 1 else ''}")
        if minutes > 0 and days == 0:
            time_parts.append(f"{minutes} 𝗆𝗂𝗇𝗎𝗍𝖾{'𝗌' if minutes != 1 else ''}")
        
        remaining_text = f" ({', '.join(time_parts)} 𝗋𝖾𝗆𝖺𝗂𝗇𝗂𝗇𝗀)" if time_parts else ""
        
        return f"**{expires_ist.strftime('%𝖽 %𝖻 %𝖸 𝖺𝗍 %𝖨:%𝖬 %𝗉 %𝖹')}**{remaining_text}"

    async def send_payment_success_notification(self, user_id: int, plan_name: str, price: str, expires_at: datetime, is_permanent: bool):
        """𝖲𝖾𝗇𝖽 𝗉𝖺𝗒𝗆𝖾𝗇𝗍 𝗌𝗎𝖼𝖼𝖾𝗌𝗌 𝗇𝗈𝗍𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝗍𝗈 𝗎𝗌𝖾𝗋"""
        expiry_text = self.format_expiry_display(expires_at, is_permanent)
        
        message = f"""💳 **𝖯𝖺𝗒𝗆𝖾𝗇𝗍 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅!** ✅

**𝖯𝗅𝖺𝗇:** {plan_name}
**𝖠𝗆𝗈𝗎𝗇𝗍 𝖯𝖺𝗂𝖽:** {price}
**𝖠𝖼𝖼𝖾𝗌𝗌 𝖳𝗒𝗉𝖾:** {'𝖯𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍' if is_permanent else '𝖯𝗋𝖾𝗆𝗂𝗎𝗆'}
**𝖤𝗑𝗉𝗂𝗋𝗒:** {expiry_text}

🎉 **𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 𝖯𝗋𝖾𝗆𝗂𝗎𝗆!** 𝖸𝗈𝗎 𝗇𝗈𝗐 𝗁𝖺𝗏𝖾 𝖺𝖼𝖼𝖾𝗌𝗌 𝗍𝗈 𝖺𝗅𝗅 𝖾𝗑𝖼𝗅𝗎𝗌𝗂𝗏𝖾 𝖿𝖾𝖺𝗍𝗎𝗋𝖾𝗌."""

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌟 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖥𝖾𝖺𝗍𝗎𝗋𝖾𝗌", callback_data="premium_features")],
            [InlineKeyboardButton("📋 𝖬𝗒 𝖲𝗎𝖻𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇", callback_data="my_subscription")],
            [InlineKeyboardButton("🆘 𝖲𝗎𝗉𝗉𝗈𝗋𝗍", url="https://t.me/your_support")]
        ])
        
        try:
            await self.client.send_message(
                user_id, 
                message, 
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            return True
        except (UserIsBlocked, InputUserDeactivated):
            return "blocked"
        except Exception as e:
            self.client.LOGGER(__name__, "PAYMENT_NOTIFY").error(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝗇𝗈𝗍𝗂𝖿𝗒 𝗎𝗌𝖾𝗋 {user_id}: {e}")
            return "error"

    def get_plans_keyboard(self):
        """𝖦𝖾𝗍 𝗉𝖺𝗒𝗆𝖾𝗇𝗍 𝗉𝗅𝖺𝗇𝗌 𝖪𝖾𝗒𝖻𝗈𝖺𝗋𝖽 𝖿𝗈𝗋 𝗈𝗐𝗇𝖾𝗋"""
        keyboard = []
        row = []
        for plan_id, plan_info in self.payment_plans.items():
            button = InlineKeyboardButton(
                f"{plan_info['name']} - {plan_info['price']}",
                callback_data=f"plan_{plan_id}"
            )
            row.append(button)
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("❌ 𝖢𝖺𝗇𝖼𝖾𝗅", callback_data="cancel_operation")])
        return InlineKeyboardMarkup(keyboard)

#========================================================================#

paid_manager = None

def get_paid_manager(client: Bot):
    global paid_manager
    if paid_manager is None:
        paid_manager = PaidUserManager(client)
    return paid_manager

#========================================================================#

@Client.on_message(filters.command(['addpaid', 'addpremium']) & filters.private)
async def add_paid_user_command(client: Bot, message: Message):
    if message.from_user.id != config.OWNER_ID:
        await message.reply_text("❌ **𝖮𝗐𝗇𝖾𝗋 𝖮𝗇𝗅𝗒 𝖢𝗈𝗆𝗆𝖺𝗇𝖽**")
        return

    manager = get_paid_manager(client)
    
    if len(message.command) == 1:
        # 𝖲𝗁𝗈𝗐 𝗉𝖺𝗒𝗆𝖾𝗇𝗍 𝗉𝗅𝖺𝗇𝗌
        help_text = """
**💰 𝖠𝖽𝖽 𝖯𝖺𝗂𝖽 𝖴𝗌𝖾𝗋 𝖲𝗒𝗌𝗍𝖾𝗆**

**𝖰𝗎𝗂𝖼𝗄 𝖯𝗅𝖺𝗇𝗌:**
"""
        for plan_id, plan_info in manager.payment_plans.items():
            help_text += f"• **{plan_info['name']}** - {plan_info['price']}\n"

        help_text += """
**𝖬𝖺𝗇𝗎𝖺𝗅 𝖠𝗎𝗍𝗁𝗈𝗋𝗂𝗓𝖺𝗍𝗂𝗈𝗇:**
`/addpaid <𝗎𝗌𝖾𝗋_𝗂𝖽> <𝗉𝗅𝖺𝗇_𝖼𝗈𝖽𝖾>`
`/addpaid <𝗎𝗌𝖾𝗋_𝗂𝖽> <𝖺𝗆𝗈𝗎𝗇𝗍> <𝗎𝗇𝗂𝗍>`
`/addpaid @𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾 1𝗆`

**𝖯𝗅𝖺𝗇 𝖢𝗈𝖽𝖾𝗌:**
- `1𝖽` - 1 𝖣𝖺𝗒 (₹50)
- `7𝖽` - 1 𝖶𝖾𝖾𝗄 (₹250) 
- `1𝗆` - 1 𝖬𝗈𝗇𝗍𝗁 (₹800)
- `3𝗆` - 3 𝖬𝗈𝗇𝗍𝗁𝗌 (₹2000)
- `1𝗒` - 1 𝖸𝖾𝖺𝗋 (₹5000)
- `𝗉𝖾𝗋𝗆` - 𝖯𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍 (₹15000)

**𝖢𝗎𝗌𝗍𝗈𝗆 𝖳𝗂𝗆𝖾 𝖴𝗇𝗂𝗍𝗌:**
𝗌=𝗌𝖾𝖼𝗈𝗇𝖽𝗌, 𝗆=𝗆𝗂𝗇𝗎𝗍𝖾𝗌, 𝗁=𝗁𝗈𝗎𝗋𝗌, 𝖽=𝖽𝖺𝗒𝗌, 𝗐=𝗐𝖾𝖾𝗄𝗌, 𝗒=𝗒𝖾𝖺𝗋𝗌

**𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌:**
• `/addpaid 123456789 1𝗆`
• `/addpaid @𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾 7𝖽`
• `/addpaid 123456789 15 𝖽` (15 𝖽𝖺𝗒𝗌)
• `/addpaid 123456789 𝗉𝖾𝗋𝗆` (𝗉𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍)
"""
        keyboard = manager.get_plans_keyboard()
        await message.reply_text(help_text, reply_markup=keyboard)
        return

    # 𝖯𝖺𝗋𝗌𝖾 𝗎𝗌𝖾𝗋 𝖨𝖣 𝗈𝗋 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾
    user_input = message.command[1]
    user_id = None
    
    try:
        if user_input.isdigit() or (user_input.startswith('-') and user_input[1:].isdigit()):
            user_id = int(user_input)
        elif user_input.startswith('@'):
            user = await client.get_users(user_input)
            user_id = user.id
        else:
            await message.reply_text("❌ **𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗎𝗌𝖾𝗋 𝖿𝗈𝗋𝗆𝖺𝗍.** 𝖴𝗌𝖾 𝗎𝗌𝖾𝗋 𝖨𝖣 𝗈𝗋 @𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾.")
            return
    except Exception as e:
        await message.reply_text(f"❌ **𝖤𝗋𝗋𝗈𝗋 𝖿𝗂𝗇𝖽𝗂𝗇𝗀 𝗎𝗌𝖾𝗋:** {e}")
        return

    # 𝖵𝖺𝗅𝗂𝖽𝖺𝗍𝖾 𝗎𝗌𝖾𝗋 𝖾𝗑𝗂𝗌𝗍𝗌
    user_validation = await manager.validate_user(user_id)
    if not user_validation['exists']:
        await message.reply_text(f"❌ **𝖴𝗌𝖾𝗋 𝗇𝗈𝗍 𝖿𝗈𝗎𝗇𝖽:** {user_validation.get('error')}")
        return

    user_info = user_validation['user']
    plan_name = "𝖢𝗎𝗌𝗍𝗈𝗆 𝖯𝗅𝖺𝗇"
    price = "𝖢𝗎𝗌𝗍𝗈𝗆 𝖠𝗆𝗈𝗎𝗇𝗍"
    expires_at_ist_display = None
    is_permanent = False

    # 𝖧𝖺𝗇𝖽𝗅𝖾 𝗉𝗅𝖺𝗇-𝖻𝖺𝗌𝖾𝖽 𝖺𝗎𝗍𝗁𝗈𝗋𝗂𝗓𝖺𝗍𝗂𝗈𝗇
    if len(message.command) >= 3:
        plan_input = message.command[2].lower()
        
        # 𝖢𝗁𝖾𝖼𝗄 𝗂𝖿 𝗂𝗍'𝗌 𝖺 𝗉𝗋𝖾𝖽𝖾𝖿𝗂𝗇𝖾𝖽 𝗉𝗅𝖺𝗇
        if plan_input in manager.payment_plans:
            plan = manager.payment_plans[plan_input]
            plan_name = plan['name']
            price = plan['price']
            is_permanent = (plan_input == 'perm')
            
            if not is_permanent:
                delta = plan['duration']
                now_ist = datetime.now(IST)
                
                # 𝖢𝗁𝖾𝖼𝗄 𝖾𝗑𝗂𝗌𝗍𝗂𝗇𝗀 𝗌𝗎𝖻𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇
                pro_doc = await client.mongodb.get_pro_user(user_id)
                if pro_doc and pro_doc.get('expires_at'):
                    existing_expires_at = pro_doc['expires_at']
                    if existing_expires_at.tzinfo is None:
                        existing_expires_at = existing_expires_at.replace(tzinfo=timezone.utc)
                    existing_expires_at_ist = existing_expires_at.astimezone(IST)
                    if existing_expires_at_ist > now_ist:
                        start_date_ist = existing_expires_at_ist
                    else:
                        start_date_ist = now_ist
                else:
                    start_date_ist = now_ist
                
                expires_at_ist_display = start_date_ist + delta
                expires_at_utc = expires_at_ist_display.astimezone(timezone.utc)
                await client.mongodb.add_pro(user_id, expires_at_utc)
            else:
                # 𝖯𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍 𝗉𝗅𝖺𝗇
                await client.mongodb.add_pro(user_id, expires_at=None)
                
        # 𝖧𝖺𝗇𝖽𝗅𝖾 𝖼𝗎𝗌𝗍𝗈𝗆 𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇
        elif len(message.command) == 4:
            try:
                amount = int(message.command[2])
                unit = message.command[3].lower()
                
                delta = manager.parse_custom_duration(amount, unit)
                if not delta:
                    await message.reply_text("❌ **𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗍𝗂𝗆𝖾 𝗎𝗇𝗂𝗍.** 𝖴𝗌𝖾: 𝗌, 𝗆, 𝗁, 𝖽, 𝗐, 𝗒")
                    return
                
                plan_name = f"𝖢𝗎𝗌𝗍𝗈𝗆 {𝖺𝗆𝗈𝗎𝗇𝗍}{𝗎𝗇𝗂𝗍}"
                price = "𝖬𝖺𝗇𝗎𝖺𝗅 𝖲𝖾𝗍𝗎𝗉"
                now_ist = datetime.now(IST)
                
                # 𝖢𝗁𝖾𝖼𝗄 𝖾𝗑𝗂𝗌𝗍𝗂𝗇𝗀 𝗌𝗎𝖻𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇
                pro_doc = await client.mongodb.get_pro_user(user_id)
                if pro_doc and pro_doc.get('expires_at'):
                    existing_expires_at = pro_doc['expires_at']
                    if existing_expires_at.tzinfo is None:
                        existing_expires_at = existing_expires_at.replace(tzinfo=timezone.utc)
                    existing_expires_at_ist = existing_expires_at.astimezone(IST)
                    if existing_expires_at_ist > now_ist:
                        start_date_ist = existing_expires_at_ist
                    else:
                        start_date_ist = now_ist
                else:
                    start_date_ist = now_ist
                
                expires_at_ist_display = start_date_ist + delta
                expires_at_utc = expires_at_ist_display.astimezone(timezone.utc)
                await client.mongodb.add_pro(user_id, expires_at_utc)
                
            except ValueError:
                await message.reply_text("❌ **𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖺𝗆𝗈𝗎𝗇𝗍.** 𝖯𝗅𝖾𝖺𝗌𝖾 𝗎𝗌𝖾 𝖺 𝗇𝗎𝗆𝖻𝖾𝗋.")
                return
        else:
            await message.reply_text("❌ **𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗉𝗅𝖺𝗇 𝖼𝗈𝖽𝖾.** 𝖢𝗁𝖾𝖼𝗄 𝗍𝗁𝖾 𝗉𝗅𝖺𝗇 𝖼𝗈𝖽𝖾𝗌 𝖺𝖻𝗈𝗏𝖾.")
            return
    else:
        await message.reply_text("❌ **𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗒 𝖺 𝗉𝗅𝖺𝗇.**")
        return

    # 𝖲𝖾𝗇𝖽 𝗇𝗈𝗍𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇𝗌
    user_notification = await manager.send_payment_success_notification(
        user_id, plan_name, price, expires_at_ist_display, is_permanent
    )

    # 𝖯𝗋𝖾𝗉𝖺𝗋𝖾 𝗈𝗐𝗇𝖾𝗋 𝗋𝖾𝗉𝗈𝗋𝗍
    owner_report = f"""✅ **𝖯𝖺𝗂𝖽 𝖴𝗌𝖾𝗋 𝖠𝖽𝖽𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒**

**𝖴𝗌𝖾𝗋:** {user_validation['name']}
**𝖨𝖣:** `{user_id}`
**𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾:** {user_validation['username']}
**𝖯𝗅𝖺𝗇:** {plan_name}
**𝖯𝗋𝗂𝖼𝖾:** {price}
**𝖤𝗑𝗉𝗂𝗋𝗒:** {manager.format_expiry_display(expires_at_ist_display, is_permanent)}

**𝖭𝗈𝗍𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇:** """

    if user_notification is True:
        owner_report += "✅ 𝖲𝖾𝗇𝗍 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒"
    elif user_notification == "blocked":
        owner_report += "⚠️ 𝖴𝗌𝖾𝗋 𝗁𝖺𝗌 𝖻𝗅𝗈𝖼𝗄𝖾𝖽 𝖻𝗈𝗍"
    else:
        owner_report += "❌ 𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝗌𝖾𝗇𝖽"

    await message.reply_text(owner_report)

#========================================================================#

@Client.on_message(filters.command(['removepaid', 'removepremium']) & filters.private)
async def remove_paid_user_command(client: Bot, message: Message):
    if message.from_user.id != config.OWNER_ID:
        await message.reply_text("❌ **𝖮𝗐𝗇𝖾𝗋 𝖮𝗇𝗅𝗒 𝖢𝗈𝗆𝗆𝖺𝗇𝖽**")
        return

    if len(message.command) != 2:
        return await message.reply_text("""
**🗑️ 𝖱𝖾𝗆𝗈𝗏𝖾 𝖯𝖺𝗂𝖽 𝖴𝗌𝖾𝗋**

**𝖴𝗌𝖺𝗀𝖾:**
`/removepaid <𝗎𝗌𝖾𝗋_𝗂𝖽>`
`/removepaid @𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾`

**𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌:**
• `/removepaid 123456789`
• `/removepaid @𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾`
""")

    try:
        user_input = message.command[1]
        user_id = None
        
        if user_input.isdigit() or (user_input.startswith('-') and user_input[1:].isdigit()):
            user_id = int(user_input)
        elif user_input.startswith('@'):
            user = await client.get_users(user_input)
            user_id = user.id
        else:
            await message.reply_text("❌ **𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗎𝗌𝖾𝗋 𝖿𝗈𝗋𝗆𝖺𝗍.**")
            return
    except Exception as e:
        await message.reply_text(f"❌ **𝖤𝗋𝗋𝗈𝗋 𝖿𝗂𝗇𝖽𝗂𝗇𝗀 𝗎𝗌𝖾𝗋:** {e}")
        return

    if not await client.mongodb.get_pro_user(user_id):
        return await message.reply_text(f"❌ **𝖴𝗌𝖾𝗋 `{user_id}` 𝗂𝗌 𝗇𝗈𝗍 𝗂𝗇 𝗍𝗁𝖾 𝗉𝖺𝗂𝖽 𝗅𝗂𝗌𝗍.**")

    await client.mongodb.remove_pro(user_id)
    
    try:
        user = await client.get_users(user_id)
        user_name = user.mention
    except:
        user_name = f"`{user_id}`"

    # 𝖭𝗈𝗍𝗂𝖿𝗒 𝗎𝗌𝖾𝗋
    try:
        await client.send_message(
            user_id,
            "🔴 **𝖸𝗈𝗎𝗋 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖠𝖼𝖼𝖾𝗌𝗌 𝖧𝖺𝗌 𝖡𝖾𝖾𝗇 𝖱𝖾𝗆𝗈𝗏𝖾𝖽**\n\n"
            "𝖸𝗈𝗎𝗋 𝗉𝖺𝗂𝖽 𝗌𝗎𝖻𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝖼𝖺𝗇𝖼𝖾𝗅𝖾𝖽.\n\n"
            "𝖳𝗈 𝗋𝖾𝗇𝖾𝗐, 𝖼𝗈𝗇𝗍𝖺𝖼𝗍 𝗍𝗁𝖾 𝗈𝗐𝗇𝖾𝗋."
        )
        notify_status = "✅ 𝖭𝗈𝗍𝗂𝖿𝗂𝖾𝖽"
    except (UserIsBlocked, InputUserDeactivated, PeerIdInvalid):
        notify_status = "⚠️ 𝖢𝗈𝗎𝗅𝖽 𝗇𝗈𝗍 𝗇𝗈𝗍𝗂𝖿𝗒 (𝖻𝗅𝗈𝖼𝗄𝖾𝖽/𝖽𝖾𝖺𝖼𝗍𝗂𝗏𝖺𝗍𝖾𝖽)"
    except Exception as e:
        notify_status = f"❌ 𝖤𝗋𝗋𝗈𝗋: {e}"

    await message.reply_text(f"""
✅ **𝖯𝖺𝗂𝖽 𝖴𝗌𝖾𝗋 𝖱𝖾𝗆𝗈𝗏𝖾𝖽**

**𝖴𝗌𝖾𝗋:** {user_name}
**𝖨𝖣:** `{user_id}`

**𝖭𝗈𝗍𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇:** {notify_status}
""")

#========================================================================#

@Client.on_message(filters.command(['paidusers', 'premiumusers']) & filters.private)
async def paid_users_list_command(client: Bot, message: Message):
    if message.from_user.id != config.OWNER_ID:
        await message.reply_text("❌ **𝖮𝗐𝗇𝖾𝗋 𝖮𝗇𝗅𝗒 𝖢𝗈𝗆𝗆𝖺𝗇𝖽**")
        return

    manager = get_paid_manager(client)
    pro_user_docs = await client.mongodb.get_pros_list()
    
    active_users = []
    expired_user_ids_to_remove = []
    now_utc = datetime.now(timezone.utc)

    for user_doc in pro_user_docs:
        expires_at = user_doc.get('expires_at')
        if expires_at and isinstance(expires_at, datetime):
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            if expires_at < now_utc:
                expired_user_ids_to_remove.append(user_doc['_id'])
                continue
        
        active_users.append(user_doc)

    # 𝖢𝗅𝖾𝖺𝗇 𝗎𝗉 𝖾𝗑𝗉𝗂𝗋𝖾𝖽 𝗎𝗌𝖾𝗋𝗌
    cleanup_notice = ""
    if expired_user_ids_to_remove:
        client.LOGGER(__name__, "PAID_USERS_CMD").info(f"𝖥𝗈𝗎𝗇𝖽 {len(expired_user_ids_to_remove)} 𝖾𝗑𝗉𝗂𝗋𝖾𝖽 𝗎𝗌𝖾𝗋𝗌. 𝖢𝗅𝖾𝖺𝗇𝗂𝗇𝗀 𝗎𝗉...")
        for user_id in expired_user_ids_to_remove:
            await client.mongodb.remove_pro(user_id)
        cleanup_notice = f"🧹 **𝖢𝗅𝖾𝖺𝗇𝖾𝖽 𝗎𝗉 {len(expired_user_ids_to_remove)} 𝖾𝗑𝗉𝗂𝗋𝖾𝖽 𝗎𝗌𝖾𝗋𝗌**\n\n"

    if not active_users:
        return await message.reply_text(f"{cleanup_notice}📭 **𝖭𝗈 𝖺𝖼𝗍𝗂𝗏𝖾 𝗉𝖺𝗂𝖽 𝗎𝗌𝖾𝗋𝗌 𝖿𝗈𝗎𝗇𝖽.**")

    formatted_users = []
    for user_doc in active_users:
        user_id = user_doc['_id']
        expires_at = user_doc.get('expires_at')
        
        if expires_at and isinstance(expires_at, datetime):
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            ist_expires_at = expires_at.astimezone(IST)
            expiry_text = f"**𝖤𝗑𝗉𝗂𝗋𝖾𝗌:** {ist_expires_at.strftime('%𝖽 %𝖻 %𝖸, %𝖧:%𝖬 %𝖹')}"
        else:
            expiry_text = "**𝖲𝗍𝖺𝗍𝗎𝗌:** 𝖯𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍 ♾️"

        try:
            user = await client.get_users(user_id)
            full_name = user.first_name + (" " + user.last_name if user.last_name else "")
            username = f"@{user.username}" if user.username else "𝖭/𝖠"
            formatted_users.append(
                f"👤 **{full_name}**\n"
                f"   ▸ **𝖨𝖣:** `{user.id}`\n"
                f"   ▸ **𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾:** {username}\n"
                f"   ▸ {expiry_text}"
            )
        except Exception:
            formatted_users.append(
                f"👤 **𝖴𝗌𝖾𝗋 𝖨𝖣:** `{user_id}`\n"
                f"   ▸ **𝖲𝗍𝖺𝗍𝗎𝗌:** 𝖨𝗇𝖿𝗈 𝗇𝗈𝗍 𝖿𝖾𝗍𝖼𝗁𝖺𝖻𝗅𝖾\n"
                f"   ▸ {expiry_text}"
            )

    response_text = f"{cleanup_notice}💰 **𝖯𝖺𝗂𝖽 𝖴𝗌𝖾𝗋𝗌 𝖫𝗂𝗌𝗍** ({len(active_users)})\n\n" + "\n\n".join(formatted_users)
    
    # 𝖲𝖾𝗇𝖽 𝗂𝗇 𝖼𝗁𝗎𝗇𝗄𝗌 𝗂𝖿 𝗍𝗈𝗈 𝗅𝗈𝗇𝗀
    for chunk in [response_text[i:i + 4096] for i in range(0, len(response_text), 4096)]:
        await message.reply_text(chunk, disable_web_page_preview=True)

#========================================================================#

@Client.on_callback_query(filters.regex(r"^plan_"))
async def handle_plan_selection(client: Bot, callback_query):
    if callback_query.from_user.id != config.OWNER_ID:
        await callback_query.answer("𝖮𝗇𝗅𝗒 𝗈𝗐𝗇𝖾𝗋 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌!", show_alert=True)
        return

    plan_id = callback_query.data.split('_')[1]
    manager = get_paid_manager(client)
    
    if plan_id not in manager.payment_plans:
        await callback_query.answer("𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗉𝗅𝖺𝗇!", show_alert=True)
        return

    await callback_query.message.edit_text(
        f"**𝖯𝗅𝖺𝗇 𝖲𝖾𝗅𝖾𝖼𝗍𝖾𝖽:** {manager.payment_plans[plan_id]['name']}\n\n"
        f"**𝖭𝗈𝗐 𝗌𝖾𝗇𝖽:** `/addpaid <𝗎𝗌𝖾𝗋_𝗂𝖽> {plan_id}`\n"
        f"**𝖤𝗑𝖺𝗆𝗉𝗅𝖾:** `/addpaid 123456789 {plan_id}`"
    )

@Client.on_callback_query(filters.regex(r"^cancel_operation$"))
async def handle_cancel_operation(client: Bot, callback_query):
    await callback_query.message.delete()
