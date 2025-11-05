from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors.pyromod import ListenerTimeout
import re

async def save_media_to_telegram(client: Client, message: Message, media_key: str):
    """𝖲𝖺𝗏𝖾 𝗆𝖾𝖽𝗂𝖺 𝖿𝗂𝗅𝖾_𝗂𝖽 𝖺𝗇𝖽 𝖺𝖼𝖼𝖾𝗌𝗌_𝗁𝖺𝗌𝗁 𝗍𝗈 𝖣𝖡"""
    try:
        if message.photo:
            # 𝖦𝖾𝗍 𝗍𝗁𝖾 𝗅𝖺𝗋𝗀𝖾𝗌𝗍 𝗉𝗁𝗈𝗍𝗈
            photo = message.photo[-1]
            media_data = {
                'file_id': photo.file_id,
                'access_hash': photo.file_unique_id,
                'type': 'photo'
            }
        elif message.video:
            video = message.video
            media_data = {
                'file_id': video.file_id,
                'access_hash': video.file_unique_id,
                'type': 'video'
            }
        else:
            return False
        
        # 𝖲𝖺𝗏𝖾 𝗍𝗈 𝖣𝖺𝗍𝖺𝖻𝖺𝗌𝖾
        client.messages[media_key] = media_data
        await client.mongodb.save_settings(client.session_name, client.get_current_settings())
        return True
        
    except Exception as e:
        print(f"Error saving media: {e}")
        return False

def get_media_display(client, key):
    """𝖦𝖾𝗍 𝗆𝖾𝖽𝗂𝖺 𝖽𝗂𝗌𝗉𝗅𝖺𝗒 𝗂𝗇𝖿𝗈"""
    media_data = client.messages.get(key)
    if not media_data:
        return "┃    <i>🚫 𝖭𝗈𝗍 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾𝖽</i>"
    
    if isinstance(media_data, dict) and 'file_id' in media_data:
        media_type = media_data.get('type', 'photo')
        if media_type == 'photo':
            return "┃    🖼️ 𝖣𝗂𝗋𝖾𝖼𝗍 𝖯𝗁𝗈𝗍𝗈"
        elif media_type == 'video':
            return "┃    📹 𝖣𝗂𝗋𝖾𝖼𝗍 𝖵𝗂𝖽𝖾𝗈"
    else:
        # 𝖴𝖱𝖫 𝖼𝖺𝗌𝖾
        url = media_data
        if len(url) > 30:
            display_url = url[:27] + "..."
        else:
            display_url = url
            
        media_type = detect_media_type(url)
        return f"┃    {media_type}\n┃    <code>{display_url}</code>"

def is_valid_media_url(url):
    """𝖢𝗁𝖾𝖼𝗄 𝗂𝖿 𝖴𝖱𝖫 𝗂𝗌 𝖺 𝗏𝖺𝗅𝗂𝖽 𝗆𝖾𝖽𝗂𝖺 𝖴𝖱𝖫"""
    # 𝖨𝗆𝖺𝗀𝖾 𝖾𝗑𝗍𝖾𝗇𝗌𝗂𝗈𝗇𝗌
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg')
    # 𝖵𝗂𝖽𝖾𝗈 𝖾𝗑𝗍𝖾𝗇𝗌𝗂𝗈𝗇𝗌  
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.gifv', '.m4v')
    
    # 𝖢𝗈𝗆𝗆𝗈𝗇 𝗆𝖾𝖽𝗂𝖺 𝗁𝗈𝗌𝗍𝗂𝗇𝗀 𝖽𝗈𝗆𝖺𝗂𝗇𝗌
    media_domains = [
        'github.com', 'raw.githubusercontent.com', 'gitlab.com',
        'telegra.ph', 'graph.org', 'imgur.com', 'i.imgur.com',
        'cdn.discordapp.com', 'media.discordapp.net',
        'i.redd.it', 'preview.redd.it',
        'ibb.co', 'imageshack.com', 'tinypic.com',
        'cdn.telegram.org', 'telegra.ph'
    ]
    
    url_lower = url.lower()
    
    # 𝖢𝗁𝖾𝖼𝗄 𝗂𝖿 𝖴𝖱𝖫 𝖾𝗇𝖽𝗌 𝗐𝗂𝗍𝗁 𝗆𝖾𝖽𝗂𝖺 𝖾𝗑𝗍𝖾𝗇𝗌𝗂𝗈𝗇
    if any(url_lower.endswith(ext) for ext in image_extensions + video_extensions):
        return True
    
    # 𝖢𝗁𝖾𝖼𝗄 𝗂𝖿 𝖴𝖱𝖫 𝖼𝗈𝗇𝗍𝖺𝗂𝗇𝗌 𝗆𝖾𝖽𝗂𝖺 𝖽𝗈𝗆𝖺𝗂𝗇
    if any(domain in url_lower for domain in media_domains):
        return True
    
    # 𝖢𝗁𝖾𝖼𝗄 𝖿𝗈𝗋 𝖽𝗂𝗋𝖾𝖼𝗍 𝗂𝗆𝖺𝗀𝖾/𝗏𝗂𝖽𝖾𝗈 𝖴𝖱𝖫𝗌 𝗐𝗂𝗍𝗁𝗈𝗎𝗍 𝖾𝗑𝗍𝖾𝗇𝗌𝗂𝗈𝗇𝗌 𝖻𝗎𝗍 𝗐𝗂𝗍𝗁 𝖼𝗈𝗆𝗆𝗈𝗇 𝗉𝖺𝗍𝗍𝖾𝗋𝗇𝗌
    if re.match(r'^https?://[^\s]+\.(png|jpg|jpeg|gif|webp|mp4|mov|avi|webm)', url_lower, re.IGNORECASE):
        return True
    
    return False

def detect_media_type(url):
    """𝖣𝖾𝗍𝖾𝖼𝗍 𝗂𝖿 𝖴𝖱𝖫 𝗂𝗌 𝗂𝗆𝖺𝗀𝖾 𝗈𝗋 𝗏𝗂𝖽𝖾𝗈"""
    url_lower = url.lower()
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg')
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.gifv', '.m4v')
    
    if any(url_lower.endswith(ext) for ext in image_extensions):
        return "🖼️ 𝖨𝗆𝖺𝗀𝖾"
    elif any(url_lower.endswith(ext) for ext in video_extensions):
        return "📹 𝖵𝗂𝖽𝖾𝗈"
    elif 'github.com' in url_lower or 'gitlab.com' in url_lower:
        return "⚡ 𝖦𝗂𝗍𝖧𝗎𝖻/𝖦𝗂𝗍𝖫𝖺𝖻 𝖬𝖾𝖽𝗂𝖺"
    elif 'telegra.ph' in url_lower or 'graph.org' in url_lower:
        return "📄 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁 𝖬𝖾𝖽𝗂𝖺"
    elif 'imgur.com' in url_lower:
        return "🌐 𝖨𝗆𝗀𝗎𝗋 𝖬𝖾𝖽𝗂𝖺"
    else:
        return "📁 𝖬𝖾𝖽𝗂𝖺 𝖥𝗂𝗅𝖾"

@Client.on_callback_query(filters.regex("^photos$"))
async def photos_panel(client: Client, query: CallbackQuery):
    await query.answer()
    
    # ─── 𝖧𝖨𝖭𝖠𝖳𝖠 𝖬𝖤𝖣𝖨𝖠 𝖯𝖠𝖭𝖤𝖫 ─────────────────────────────────────────
    msg = f"""
╭───「 🌸 **𝖧𝖨𝖭𝖠𝖳𝖠 𝖬𝖤𝖣𝖨𝖠 𝖬𝖠𝖭𝖠𝖦𝖤𝖬𝖤𝖭𝖳** 」
│
├─ 🎴 **𝖲𝖳𝖠𝖱𝖳 𝖬𝖤𝖣𝖨𝖠**
{get_media_display(client, 'START_PHOTO')}
│
├─ 📢 **𝖥𝖮𝖱𝖢𝖤 𝖲𝖴𝖡𝖲𝖢𝖱𝖨𝖡𝖤**  
{get_media_display(client, 'FSUB_PHOTO')}
│
├─ ⏳ **𝖵𝖤𝖱𝖨𝖥𝖨𝖢𝖠𝖳𝖨𝖮𝖭 𝖬𝖤𝖣𝖨𝖠**
{get_media_display(client, 'VERIFY_PHOTO')}
│
╰───「 🔮 *𝖧𝗂𝗇𝖺𝗍𝖺 𝗏𝟤.𝟢* 」───────

✨ **𝖣𝗂𝗋𝖾𝖼𝗍 𝖴𝗉𝗅𝗈𝖺𝖽:** 𝖯𝗁𝗈𝗍𝗈𝗌 & 𝖵𝗂𝖽𝖾𝗈𝗌
🌐 **𝖴𝖱𝖫 𝖲𝗎𝗉𝗉𝗈𝗋𝗍:** 𝖦𝗂𝗍𝖧𝗎𝖻, 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁, 𝖨𝗆𝗀𝗎𝗋, 𝖢𝖣𝖭
⚡ **𝖥𝗎𝗅𝗅 𝖥𝗅𝖾𝗑𝗂𝖻𝗂𝗅𝗂𝗍𝗒:** 𝖢𝗁𝗈𝗈𝗌𝖾 𝗒𝗈𝗎𝗋 𝗉𝗋𝖾𝖿𝖾𝗋𝗋𝖾𝖽 𝗆𝖾𝗍𝗁𝗈𝖽"""
    
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('🎴 𝖲𝗍𝖺𝗋𝗍', callback_data='setphoto_START_PHOTO'),
            InlineKeyboardButton('📢 𝖥𝖲𝗎𝖻', callback_data='setphoto_FSUB_PHOTO'),
            InlineKeyboardButton('⏳ 𝖵𝖾𝗋𝗂𝖿𝗒', callback_data='setphoto_VERIFY_PHOTO')
        ],
        [
            InlineKeyboardButton('📹 𝖬𝖾𝖽𝗂𝖺 𝖨𝗇𝖿𝗈', callback_data='media_info'),
            InlineKeyboardButton('🔄 𝖱𝖾𝖿𝗋𝖾𝗌𝗁', callback_data='photos')
        ],
        [
            InlineKeyboardButton('𓆩˹𓆃 𝖡𝖺𝖼𝗄', callback_data='settings')
        ]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^setphoto_"))
async def set_photo(client: Client, query: CallbackQuery):
    await query.answer()
    
    photo_key = query.data.split("_", 1)[1]
    
    key_name_map = {
        "START_PHOTO": "𝖲𝗍𝖺𝗋𝗍 𝖬𝖾𝖽𝗂𝖺",
        "FSUB_PHOTO": "𝖥𝗈𝗋𝖼𝖾 𝖲𝗎𝖻𝗌𝖼𝗋𝗂𝖻𝖾 𝖬𝖾𝖽𝗂𝖺", 
        "VERIFY_PHOTO": "𝖵𝖾𝗋𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝖬𝖾𝖽𝗂𝖺"
    }
    
    try:
        ask_msg = await client.ask(
            chat_id=query.from_user.id,
            text=f"""**📤 𝖲𝖾𝗇𝖽 𝗇𝖾𝗐 𝗆𝖾𝖽𝗂𝖺 𝖿𝗈𝗋 {key_name_map.get(photo_key, photo_key)}**

✨ **𝖣𝗂𝗋𝖾𝖼𝗍 𝖴𝗉𝗅𝗈𝖺𝖽:**
• 𝖲𝖾𝗇𝖽 𝖺 𝗉𝗁𝗈𝗍𝗈 𝗈𝗋 𝗏𝗂𝖽𝖾𝗈 𝖽𝗂𝗋𝖾𝖼𝗍𝗅𝗒

🌐 **𝖴𝖱𝖫 𝖲𝗎𝗉𝗉𝗈𝗋𝗍:**
• 𝖦𝗂𝗍𝖧𝗎𝖻, 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁, 𝖨𝗆𝗀𝗎𝗋, 𝖢𝖣𝖭
• 𝖣𝗂𝗋𝖾𝖼𝗍 𝗂𝗆𝖺𝗀𝖾/𝗏𝗂𝖽𝖾𝗈 𝗅𝗂𝗇𝗄𝗌

𝖳𝗒𝗉𝖾 `𝗋𝖾𝗆𝗈𝗏𝖾` 𝗍𝗈 𝖼𝗅𝖾𝖺𝗋 𝗈𝗋 `𝖼𝖺𝗇𝖼𝖾𝗅` 𝗍𝗈 𝗀𝗈 𝖻𝖺𝖼𝗄.""",
            filters=filters.photo | filters.video | filters.text,
            timeout=60
        )

        if ask_msg.text:
            text = ask_msg.text.lower()
            if text == 'cancel':
                await ask_msg.reply("❌ 𝖮𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽.")
            elif text == 'remove':
                client.messages[photo_key] = ""
                await client.mongodb.save_settings(client.session_name, client.get_current_settings())
                await ask_msg.reply(f"✅ 𝖬𝖾𝖽𝗂𝖺 𝖿𝗈𝗋 `{key_name_map.get(photo_key, photo_key)}` 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗋𝖾𝗆𝗈𝗏𝖾𝖽.")
            else:
                url = ask_msg.text.strip()
                if is_valid_media_url(url):
                    client.messages[photo_key] = url
                    await client.mongodb.save_settings(client.session_name, client.get_current_settings())
                    
                    # 𝖣𝖾𝗍𝖾𝖼𝗍 𝗆𝖾𝖽𝗂𝖺 𝗍𝗒𝗉𝖾 𝖿𝗈𝗋 𝖻𝖾𝗍𝗍𝖾𝗋 𝖿𝖾𝖾𝖽𝖻𝖺𝖼𝗄
                    media_type = detect_media_type(url)
                    await ask_msg.reply(f"✅ **{media_type}** 𝖿𝗈𝗋 `{key_name_map.get(photo_key, photo_key)}` 𝗎𝗉𝖽𝖺𝗍𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒!")
                else:
                    await ask_msg.reply("❌ **𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖴𝖱𝖫.** 𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗏𝖺𝗅𝗂𝖽 𝖽𝗂𝗋𝖾𝖼𝗍 𝗂𝗆𝖺𝗀𝖾/𝗏𝗂𝖽𝖾𝗈 𝖴𝖱𝖫 𝗈𝗋 𝗌𝖾𝗇𝖽 𝖺 𝗉𝗁𝗈𝗍𝗈/𝗏𝗂𝖽𝖾𝗈 𝖽𝗂𝗋𝖾𝖼𝗍𝗅𝗒.")
        
        elif ask_msg.photo or ask_msg.video:
            success = await save_media_to_telegram(client, ask_msg, photo_key)
            if success:
                media_type = "🖼️ 𝖯𝗁𝗈𝗍𝗈" if ask_msg.photo else "📹 𝖵𝗂𝖽𝖾𝗈"
                await ask_msg.reply(f"✅ **{media_type}** 𝖿𝗈𝗋 `{key_name_map.get(photo_key, photo_key)}` 𝗎𝗉𝗅𝗈𝖺𝖽𝖾𝖽 𝖺𝗇𝖽 𝗌𝖺𝗏𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒!")
            else:
                await ask_msg.reply("❌ **𝖤𝗋𝗋𝗈𝗋 𝗌𝖺𝗏𝗂𝗇𝗀 𝗆𝖾𝖽𝗂𝖺.** 𝖯𝗅𝖾𝖺𝗌𝖾 𝗍𝗋𝗒 𝖺𝗀𝖺𝗂𝗇.")

    except ListenerTimeout:
        await query.message.reply("⏰ 𝖳𝗂𝗆𝖾𝗈𝗎𝗍. 𝖮𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽.")
    except Exception as e:
        await query.message.reply(f"❌ 𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {e}")

    await photos_panel(client, query) # 𝖦𝗈 𝖻𝖺𝖼𝗄 𝗍𝗈 𝗍𝗁𝖾 𝗋𝖾𝖿𝗂𝗇𝖾𝖽 𝗉𝖺𝗇𝖾𝗅

@Client.on_callback_query(filters.regex("^media_info$"))
async def media_info(client: Client, query: CallbackQuery):
    await query.answer()
    
    msg = """
╭───「 📚 𝖬𝖤𝖣𝖨𝖠 𝖨𝖭𝖥𝖮𝖱𝖬𝖠𝖳𝖨𝖮𝖭 」───
│
├─ 🎯 **𝖣𝗂𝗋𝖾𝖼𝗍 𝖴𝗉𝗅𝗈𝖺𝖽:**
│  • 𝖲𝗂𝗆𝗉𝗅𝗒 𝗌𝖾𝗇𝖽 𝗉𝗁𝗈𝗍𝗈/𝗏𝗂𝖽𝖾𝗈
│  • 𝖠𝗎𝗍𝗈-𝗌𝖺𝗏𝖾𝗌 𝗍𝗈 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆
│  • 𝖥𝖺𝗌𝗍 𝖺𝗇𝖽 𝖾𝖺𝗌𝗒
│
├─ 🌸 **𝖴𝖱𝖫 𝖲𝗎𝗉𝗉𝗈𝗋𝗍:**
│  • 𝖦𝗂𝗍𝖧𝗎𝖻, 𝖦𝗂𝗍𝖫𝖺𝖻, 𝖨𝗆𝗀𝗎𝗋
│  • 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁, 𝖦𝗋𝖺𝗉𝗁.𝗈𝗋𝗀
│  • 𝖢𝖣𝖭 𝗅𝗂𝗇𝗄𝗌, 𝖣𝗂𝗋𝖾𝖼𝗍 𝗎𝗋𝗅𝗌
│
├─ 📹 **𝖲𝗎𝗉𝗉𝗈𝗋𝗍𝖾𝖽 𝖥𝗈𝗋𝗆𝖺𝗍𝗌:**
│  • 𝖯𝗁𝗈𝗍𝗈𝗌: JPG, PNG, GIF, WEBP
│  • 𝖵𝗂𝖽𝖾𝗈𝗌: MP4, MOV, AVI, WEBM
│
╰───「 🔮 *𝖧𝗂𝗇𝖺𝗍𝖺* 」─────────"""
    
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('𓆩˹𓆃 𝖡𝖺𝖼𝗄', callback_data='photos')
        ]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)
