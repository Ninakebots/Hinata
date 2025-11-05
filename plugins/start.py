from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import humanize
import time
import secrets
import random
import string as rohit_string
from datetime import datetime
from zoneinfo import ZoneInfo
from plugins.shortner import get_short
import config

IST = ZoneInfo("Asia/Kolkata")
CACHE_TTL_SECONDS = 300

@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    user_state, _ = await client.mongodb.get_user_state(user_id)
    if user_state is None: return await message.reply("**❌ 𝖠 𝖼𝗋𝗂𝗍𝗂𝖼𝖺𝗅 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽.**")
    if user_state.get('banned', False): return await message.reply("**🔴 𝖸𝗈𝗎 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖻𝖺𝗇𝗇𝖾𝖽 𝖿𝗋𝗈𝗆 𝗎𝗌𝗂𝗇𝗀 𝗍𝗁𝗂𝗌 𝖻𝗈𝗍!**")

    if len(message.command) > 1:
        payload = message.command[1]

        if payload.startswith("verify_"):
            token = payload.split("_", 1)[1]
            verify_status = await client.mongodb.get_verify_status(user_id)
            
            if verify_status.get('verify_token') != token:
                return await message.reply("**⚠️ 𝖫𝗂𝗇𝗄 𝖤𝗑𝗉𝗂𝗋𝖾𝖽 𝗈𝗋 𝖨𝗇𝗏𝖺𝗅𝗂𝖽.**\n𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗍𝗁𝖾 𝖿𝗂𝗅𝖾 𝖺𝗀𝖺𝗂𝗇.")

            verify_status['is_verified'] = True
            verify_status['verified_time'] = time.time()
            verify_status['verify_token'] = ""
            await client.mongodb.update_verify_status(user_id, verify_status)
            await client.mongodb.increment_verify_count()
            
            file_payload = verify_status.get('file_payload')
            buttons = [[InlineKeyboardButton("✖️ 𝖢𝗅𝗈𝗌𝖾", callback_data="close")]]
            if file_payload:
                buttons.insert(0, [InlineKeyboardButton("✅ 𝖦𝖾𝗍 𝖸𝗈𝗎𝗋 𝖥𝗂𝗅𝖾𝗌", callback_data=f"get_file_{file_payload}")])

            return await message.reply(
                f"**✅ 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝗏𝖾𝗋𝗂𝖿𝗂𝖾𝖽!**\n\n𝖸𝗈𝗎𝗋 𝖺𝖼𝖼𝖾𝗌𝗌 𝗂𝗌 𝗏𝖺𝗅𝗂𝖽 𝖿𝗈𝗋 𝗍𝗁𝖾 𝗇𝖾𝗑𝗍 **{client.verify_expire} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌**.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        base64_string = payload
        
        if user_id in client.admins or user_state.get('is_pro', False):
            return await send_files(client, user_id, base64_string)

        verify_status = await client.mongodb.get_verify_status(user_id)
        is_still_verified = verify_status.get('is_verified', False) and (time.time() - verify_status.get('verified_time', 0)) < client.verify_expire

        if is_still_verified:
            return await send_files(client, user_id, base64_string)
        else:
            token = ''.join(random.choices(rohit_string.ascii_letters + rohit_string.digits, k=10))
            
            verify_status['verify_token'] = token
            verify_status['file_payload'] = base64_string
            await client.mongodb.update_verify_status(user_id, verify_status)
            
            link = f"https://t.me/{client.username}?start=verify_{token}"
            short_link = get_short(link, client)

            btn = [
                [InlineKeyboardButton("𝖮𝗉𝖾𝗇 𝖫𝗂𝗇𝗄", url=short_link), InlineKeyboardButton("📚 𝖳𝗎𝗍𝗈𝗋𝗂𝖺𝗅", url=config.TUT_VID)],
                [InlineKeyboardButton("𝖡𝗎𝗒 𝖯𝗋𝖾𝗆𝗂𝗎𝗆", url="https://t.me/Rtx_Contect_bot")]
            ]
            verify_photo = client.messages.get("VERIFY_PHOTO", "")
            
            # --- UPDATED WITH SPECIAL FONT ---
            caption = f"""**𝖵𝖾𝗋𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝖱𝖾𝗊𝗎𝗂𝗋𝖾𝖽**

‼️ **𝖸𝗈𝗎'𝗋𝖾 𝖭𝗈𝗍 𝖵𝖾𝗋𝗂𝖿𝗂𝖾𝖽** ‼️

**𝖯𝗅𝖾𝖺𝗌𝖾 𝖼𝗈𝗆𝗉𝗅𝖾𝗍𝖾 𝗏𝖾𝗋𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝗍𝗈 𝖺𝖼𝖼𝖾𝗌𝗌 𝖿𝗂𝗅𝖾𝗌:**
• 𝖢𝗅𝗂𝖼𝗄 "𝖮𝗉𝖾𝗇 𝖫𝗂𝗇𝗄" 𝖻𝖾𝗅𝗈𝗐
• 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝖾 𝗍𝗁𝖾 𝗏𝖾𝗋𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝗌𝗍𝖾𝗉𝗌
• 𝖦𝖾𝗍 **{client.verify_expire} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌** 𝗈𝖿 𝖺𝖼𝖼𝖾𝗌𝗌 ✅

**𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖡𝖾𝗇𝖾𝖿𝗂𝗍𝗌:**
• 𝖭𝗈 𝗏𝖾𝗋𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝗋𝖾𝗊𝗎𝗂𝗋𝖾𝖽
• 𝖭𝗈 𝗌𝗁𝗈𝗋𝗍 𝗅𝗂𝗇𝗄𝗌
• 𝖴𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 𝖺𝖼𝖼𝖾𝗌𝗌
• 𝖯𝗋𝗂𝗈𝗋𝗂𝗍𝗒 𝗌𝗎𝗉𝗉𝗈𝗋𝗍**"""
            
            if verify_photo:
                await message.reply_photo(photo=verify_photo, caption=caption, reply_markup=InlineKeyboardMarkup(btn))
            else:
                await message.reply(text=caption, reply_markup=InlineKeyboardMarkup(btn))
            return
            
    else:
        buttons = [
            [InlineKeyboardButton("𝖠𝖻𝗈𝗎𝗍", callback_data="about"), InlineKeyboardButton("✖️ 𝖢𝗅𝗈𝗌𝖾", callback_data='close')]
        ]
        if user_id in client.admins:
            buttons.insert(0, [InlineKeyboardButton("𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌", callback_data="settings")])
        
        photo = client.messages.get("START_PHOTO", "")
        start_caption = client.messages.get('START', '**👋 𝖶𝖾𝗅𝖼𝗈𝗆𝖾!**').format(
            first=message.from_user.first_name, 
            last=message.from_user.last_name, 
            username=f"@{message.from_user.username}" if message.from_user.username else "𝖭/𝖠", 
            mention=message.from_user.mention, 
            id=user_id
        )
        
        try:
            if photo: 
                await message.reply_photo(
                    photo=photo, 
                    caption=start_caption, 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            else: 
                await message.reply_text(
                    text=start_caption, 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
        except Exception as e: 
            client.LOGGER(__name__, "WELCOME").error(f"𝖤𝗋𝗋𝗈𝗋 𝗌𝖾𝗇𝖽𝗂𝗇𝗀 𝗐𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 {user_id}: {e}")

@Client.on_callback_query(filters.regex(r"^get_file_"))
async def get_file_callback_handler(client: Client, query: CallbackQuery):
    base64_string = query.data.split("_", 2)[2]
    await query.answer("**𝖯𝗅𝖾𝖺𝗌𝖾 𝗐𝖺𝗂𝗍, 𝗌𝖾𝗇𝖽𝗂𝗇𝗀 𝗒𝗈𝗎𝗋 𝖿𝗂𝗅𝖾(𝗌)...**", show_alert=True)
    await send_files(client, query.from_user.id, base64_string)
    await query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("𝖣𝗈𝗇𝖾", callback_data="close")]
        ])
    )

async def get_user_state_with_cache(client: Client, user_id: int):
    now = time.time()
    state, pro_expires_at = await client.mongodb.get_user_state(user_id)
    if state is not None:
        client.user_cache[user_id] = {'state': state, 'timestamp': now, 'pro_expires_at': pro_expires_at}
    return state

@Client.on_message(filters.command('request') & filters.private)
async def request_command(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in client.admins or user_id == client.owner: 
        return await message.reply_text("**𝖠𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇𝗇𝗈𝗍 𝗆𝖺𝗄𝖾 𝗋𝖾𝗊𝗎𝖾𝗌𝗍𝗌.**")
    
    user_state = await get_user_state_with_cache(client, user_id)
    if user_state is None or not user_state.get('is_pro', False): 
        return await message.reply(
            "**𝖮𝗇𝗅𝗒 𝗉𝗋𝖾𝗆𝗂𝗎𝗆 𝗎𝗌𝖾𝗋𝗌 𝖼𝖺𝗇 𝗆𝖺𝗄𝖾 𝗋𝖾𝗊𝗎𝖾𝗌𝗍𝗌.**", 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("𝖡𝗎𝗒 𝖯𝗋𝖾𝗆𝗂𝗎𝗆", url="https://t.me/Rtx_Contect_bot")]
            ])
        )
    
    if len(message.command) < 2: 
        return await message.reply("**𝖴𝗌𝖺𝗀𝖾:**\n`/request <𝖼𝗈𝗇𝗍𝖾𝗇𝗍 𝗇𝖺𝗆𝖾>`")
    
    owner_message = f"""**𝖭𝖾𝗐 𝖱𝖾𝗊𝗎𝖾𝗌𝗍**

**👤 𝖥𝗋𝗈𝗆:** {message.from_user.mention} (`{user_id}`)
**📋 𝖱𝖾𝗊𝗎𝖾𝗌𝗍:** `{' '.join(message.command[1:])}`"""
    
    try:
        await client.send_message(client.owner, owner_message)
        await message.reply("**𝖸𝗈𝗎𝗋 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝖾𝗇𝗍!**")
    except Exception as e:
        client.LOGGER(__name__, "REQUEST").error(f"𝖢𝗈𝗎𝗅𝖽 𝗇𝗈𝗍 𝖿𝗈𝗋𝗐𝖺𝗋𝖽 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝖿𝗋𝗈𝗆 {user_id}: {e}")
        await message.reply("**𝖲𝗈𝗋𝗋𝗒, 𝗍𝗁𝖾𝗋𝖾 𝗐𝖺𝗌 𝖺𝗇 𝖾𝗋𝗋𝗈𝗋 𝗌𝖾𝗇𝖽𝗂𝗇𝗀 𝗒𝗈𝗎𝗋 𝗋𝖾𝗊𝗎𝖾𝗌𝗍.**")

@Client.on_message(filters.command('profile') & filters.private)
async def my_plan(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in client.admins or user_id == client.owner: 
        return await message.reply_text("**𝖸𝗈𝗎'𝗋𝖾 𝖺𝗇 𝖺𝖽𝗆𝗂𝗇. 𝖸𝗈𝗎 𝗁𝖺𝗏𝖾 𝖺𝖼𝖼𝖾𝗌𝗌 𝗍𝗈 𝖾𝗏𝖾𝗋𝗒𝗍𝗁𝗂𝗇𝗀!**")
    
    user_state = await get_user_state_with_cache(client, user_id)
    if user_state is None: 
        return await message.reply("**𝖢𝗈𝗎𝗅𝖽 𝗇𝗈𝗍 𝖿𝖾𝗍𝖼𝗁 𝗉𝗋𝗈𝖿𝗂𝗅𝖾 𝖽𝗎𝖾 𝗍𝗈 𝖺 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾 𝖾𝗋𝗋𝗈𝗋.**")
    
    if user_state.get('is_pro', False):
        pro_data = await client.mongodb.get_pro_user(user_id)
        expires_at = pro_data.get('expires_at') if pro_data else None
        
        if expires_at and isinstance(expires_at, datetime):
            if expires_at.tzinfo is None: 
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            expiry_text = f"**𝖤𝗑𝗉𝗂𝗋𝖾𝗌 𝗂𝗇:** {humanize.naturaldelta(expires_at - datetime.now(timezone.utc))}"
        else: 
            expiry_text = "**𝖤𝗑𝗉𝗂𝗋𝗒:** 𝖯𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍"
        
        plan_text = f"""**𝖸𝗈𝗎𝗋 𝖯𝗋𝗈𝖿𝗂𝗅𝖾**

**𝖯𝗅𝖺𝗇:** 𝖯𝗋𝖾𝗆𝗂𝗎𝗆
{expiry_text}
**𝖠𝖽𝗌:** 𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽
**𝖱𝖾𝗊𝗎𝖾𝗌𝗍𝗌:** 𝖤𝗇𝖺𝖻𝗅𝖾𝖽

**𝖳𝗁𝖺𝗇𝗄 𝗒𝗈𝗎 𝖿𝗈𝗋 𝖻𝖾𝗂𝗇𝗀 𝖺 𝗉𝗋𝖾𝗆𝗂𝗎𝗆 𝗎𝗌𝖾𝗋!**"""
    else:
        plan_text = f"""**👤 𝖸𝗈𝗎𝗋 𝖯𝗋𝗈𝖿𝗂𝗅𝖾**

**𝖯𝗅𝖺𝗇:** 𝖥𝗋𝖾𝖾
**𝖠𝖽𝗌:** 𝖤𝗇𝖺𝖻𝗅𝖾𝖽
**𝖱𝖾𝗊𝗎𝖾𝗌𝗍𝗌:** 𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽

**𝖴𝗇𝗅𝗈𝖼𝗄 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖡𝖾𝗇𝖾𝖿𝗂𝗍𝗌:**
• 𝖭𝗈 𝖺𝖽𝗏𝖾𝗋𝗍𝗂𝗌𝖾𝗆𝖾𝗇𝗍𝗌
• 𝖣𝗂𝗋𝖾𝖼𝗍 𝖿𝗂𝗅𝖾 𝖺𝖼𝖼𝖾𝗌𝗌
• 𝖱𝖾𝗊𝗎𝖾𝗌𝗍 𝖿𝖾𝖺𝗍𝗎𝗋𝖾
• 𝖯𝗋𝗂𝗈𝗋𝗂𝗍𝗒 𝗌𝗎𝗉𝗉𝗈𝗋𝗍

**𝖢𝗈𝗇𝗍𝖺𝖼𝗍:** @Rtx_Contect_bot"""
    
    await message.reply_text(plan_text)
