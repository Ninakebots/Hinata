from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.pyromod import ListenerTimeout
import re

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
    
    def get_photo(key):
        photo_url = client.messages.get(key)
        if not photo_url:
            return "┃    <i>🚫 𝖭𝗈𝗍 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾𝖽</i>"
        
        # 𝖳𝗋𝗎𝗇𝖼𝖺𝗍𝖾 𝗅𝗈𝗇𝗀 𝖴𝖱𝖫𝗌 𝖿𝗈𝗋 𝖽𝗂𝗌𝗉𝗅𝖺𝗒
        if len(photo_url) > 30:
            display_url = photo_url[:27] + "..."
        else:
            display_url = photo_url
            
        media_type = detect_media_type(photo_url)
        return f"┃    {media_type}\n┃    <code>{display_url}</code>"

    # ─── 𝖧𝖨𝖭𝖠𝖳𝖠 𝖬𝖤𝖣𝖨𝖠 𝖯𝖠𝖭𝖤𝖫 ─────────────────────────────────────────
    msg = f"""
╭───「 🌸 **𝖧𝖨𝖭𝖠𝖳𝖠 𝖬𝖤𝖣𝖨𝖠 𝖬𝖠𝖭𝖠𝖦𝖤𝖬𝖤𝖭𝖳** 」
│
├─ 🎴 **𝖲𝖳𝖠𝖱𝖳 𝖬𝖤𝖣𝖨𝖠**
{get_photo('START_PHOTO')}
│
├─ 📢 **𝖥𝖮𝖱𝖢𝖤 𝖲𝖴𝖡𝖲𝖢𝖱𝖨𝖡𝖤**  
{get_photo('FSUB_PHOTO')}
│
├─ ⏳ **𝖵𝖤𝖱𝖨𝖥𝖨𝖢𝖠𝖳𝖨𝖮𝖭 𝖬𝖤𝖣𝖨𝖠**
{get_photo('VERIFY_PHOTO')}
│
╰───「 🔮 *𝖧𝗂𝗇𝖺𝗍𝖺 𝗏𝟤.𝟢* 」───────

✨ **𝖲𝗎𝗉𝗉𝗈𝗋𝗍𝖾𝖽 𝖥𝗈𝗋𝗆𝖺𝗍𝗌:** 𝖨𝗆𝖺𝗀𝖾𝗌 • 𝖵𝗂𝖽𝖾𝗈𝗌 • 𝖦𝖨𝖥𝗌
🌐 **𝖲𝗈𝗎𝗋𝖼𝖾𝗌:** 𝖦𝗂𝗍𝖧𝗎𝖻, 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁, 𝖨𝗆𝗀𝗎𝗋, 𝖢𝖣𝖭, 𝖣𝗂𝗋𝖾𝖼𝗍 𝖫𝗂𝗇𝗄𝗌
⚡ **𝖲𝗆𝖺𝗋𝗍 𝖣𝖾𝗍𝖾𝖼𝗍𝗂𝗈𝗇:** 𝖠𝗎𝗍𝗈-𝖽𝖾𝗍𝖾𝖼𝗍𝗌 𝗆𝖾𝖽𝗂𝖺 𝗍𝗒𝗉𝖾"""
    
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
            text=f"**📤 𝖲𝖾𝗇𝖽 𝗇𝖾𝗐 𝗆𝖾𝖽𝗂𝖺 𝖴𝖱𝖫 𝖿𝗈𝗋 {key_name_map.get(photo_key, photo_key)}**\n\n✨ **𝖲𝗎𝗉𝗉𝗈𝗋𝗍𝖾𝖽 𝖥𝗈𝗋𝗆𝖺𝗍𝗌:**\n• 𝖨𝗆𝖺𝗀𝖾𝗌: `𝗃𝗉𝗀, 𝗉𝗇𝗀, 𝗀𝗂𝖿, 𝗐𝖾𝖻𝗉`\n• 𝖵𝗂𝖽𝖾𝗈𝗌: `𝗆𝗉𝟦, 𝗀𝗂𝖿, 𝗐𝖾𝖻𝗆`\n\n🌐 **𝖲𝗎𝗉𝗉𝗈𝗋𝗍𝖾𝖽 𝖲𝗈𝗎𝗋𝖼𝖾𝗌:**\n• 𝖦𝗂𝗍𝖧𝗎𝖻, 𝖦𝗂𝗍𝖫𝖺𝖻, 𝖨𝗆𝗀𝗎𝗋, 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁\n• 𝖢𝖣𝖭 𝗅𝗂𝗇𝗄𝗌, 𝖣𝗂𝗋𝖾𝖼𝗍 𝗂𝗆𝖺𝗀𝖾 𝖴𝖱𝖫𝗌\n• 𝖢𝗅𝗈𝗎𝖽 𝗌𝗍𝗈𝗋𝖺𝗀𝖾 𝗅𝗂𝗇𝗄𝗌\n\n𝖳𝗒𝗉𝖾 `𝗋𝖾𝗆𝗈𝗏𝖾` 𝗍𝗈 𝖼𝗅𝖾𝖺𝗋 𝗈𝗋 `𝖼𝖺𝗇𝖼𝖾𝗅` 𝗍𝗈 𝗀𝗈 𝖻𝖺𝖼𝗄.",
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
                    await ask_msg.reply("❌ **𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖴𝖱𝖫.** 𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗏𝖺𝗅𝗂𝖽 𝖽𝗂𝗋𝖾𝖼𝗍 𝗂𝗆𝖺𝗀𝖾/𝗏𝗂𝖽𝖾𝗈 𝖴𝖱𝖫.\n\n**𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌:**\n• `https://github.com/user/repo/image.png`\n• `https://telegra.ph/file/example.jpg`\n• `https://i.imgur.com/example.png`")
        
        elif ask_msg.photo or ask_msg.video:
            await ask_msg.reply("❌ **𝖣𝗂𝗋𝖾𝖼𝗍 𝗆𝖾𝖽𝗂𝖺 𝗎𝗉𝗅𝗈𝖺𝖽𝗌 𝖺𝗋𝖾 𝗇𝗈𝗍 𝖺𝗅𝗅𝗈𝗐𝖾𝖽.** 𝖯𝗅𝖾𝖺𝗌𝖾 𝗎𝗉𝗅𝗈𝖺𝖽 𝗒𝗈𝗎𝗋 𝗆𝖾𝖽𝗂𝖺 𝗍𝗈 𝖦𝗂𝗍𝖧𝗎𝖻, 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁, 𝗈𝗋 𝖨𝗆𝗀𝗎𝗋 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗆𝖾 𝗍𝗁𝖾 𝗋𝖾𝗌𝗎𝗅𝗍𝗂𝗇𝗀 𝗅𝗂𝗇𝗄.", disable_web_page_preview=True)

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
├─ 🌸 **𝖧𝗈𝗐 𝗍𝗈 𝗀𝖾𝗍 𝖦𝗂𝗍𝖧𝗎𝖻 𝖬𝖾𝖽𝗂𝖺 𝖴𝖱𝖫:**
│  𝟣. 𝖦𝗈 𝗍𝗈 𝖦𝗂𝗍𝖧𝗎𝖻.𝖼𝗈𝗆
│  𝟤. 𝖴𝗉𝗅𝗈𝖺𝖽 𝗂𝗆𝖺𝗀𝖾/𝗏𝗂𝖽𝖾𝗈 𝗍𝗈 𝗋𝖾𝗉𝗈
│  𝟥. 𝖢𝗅𝗂𝖼𝗄 𝗈𝗇 𝗍𝗁𝖾 𝖿𝗂𝗅𝖾
│  𝟦. 𝖢𝗈𝗉𝗒 "𝖱𝖺𝗐" 𝖴𝖱𝖫
│  𝟧. 𝖯𝖺𝗌𝗍𝖾 𝗁𝖾𝗋𝖾
│
├─ 📄 **𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗉𝗁:**
│  • 𝖦𝗈 𝗍𝗈: 𝖳𝖾𝗅𝖾𝗀𝗋𝖺.𝗉𝗁
│  • 𝖴𝗉𝗅𝗈𝖺𝖽 𝗆𝖾𝖽𝗂𝖺
│  • 𝖢𝗈𝗉𝗒 𝗅𝗂𝗇𝗄
│
├─ 🌐 **𝖨𝗆𝗀𝗎𝗋:**
│  • 𝖦𝗈 𝗍𝗈: 𝖨𝗆𝗀𝗎𝗋.𝖼𝗈𝗆
│  • 𝖴𝗉𝗅𝗈𝖺𝖽 𝗂𝗆𝖺𝗀𝖾
│  • 𝖢𝗈𝗉𝗒 𝖽𝗂𝗋𝖾𝖼𝗍 𝗅𝗂𝗇𝗄
│
╰───「 🔮 *𝖧𝗂𝗇𝖺𝗍𝖺* 」─────────"""
    
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('𓆩˹𓆃 𝖡𝖺𝖼𝗄', callback_data='photos')
        ]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)
