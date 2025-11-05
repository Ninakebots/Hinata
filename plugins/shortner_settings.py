from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.pyromod import ListenerTimeout

# Import the main settings panel to navigate back
from .settings import settings_panel

# This function displays the shortener sub-menu
async def shortner_settings_main(client: Client, query: CallbackQuery):
    await query.answer()
    
    # Format API key for display (masked for security)
    if client.short_api and len(client.short_api) > 8:
        api_key_display = f"{'*' * 12}{client.short_api[-4:]}"
    elif client.short_api:
        api_key_display = "𝖬𝖺𝗌𝗄𝖾𝖽"
    else:
        api_key_display = "𝖭𝗈𝗍 𝖲𝖾𝗍"
    
    # Format short URL for display
    short_url_display = f"`{client.short_url}`" if client.short_url else "𝖭𝗈𝗍 𝖲𝖾𝗍"
    
    msg = f"""**🔗 𝖲𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖺𝗍𝗂𝗈𝗇**

**✓ 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖴𝖱𝖫:** {short_url_display}
**✓ 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖠𝖯𝖨 𝖪𝖾𝗒:** `{api_key_display}`

**𝖬𝖺𝗇𝖺𝗀𝖾 𝗒𝗈𝗎𝗋 𝖴𝖱𝖫 𝗌𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌.**
**𝖢𝗁𝖺𝗇𝗀𝖾𝗌 𝖺𝗋𝖾 𝖺𝗉𝗉𝗅𝗂𝖾𝖽 𝗂𝗇𝗌𝗍𝖺𝗇𝗍𝗅𝗒 𝖺𝗇𝖽 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝗌𝖺𝗏𝖾𝖽.**"""
    
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('✗ 𝖢𝗁𝖺𝗇𝗀𝖾 𝖴𝖱𝖫', callback_data='change_short_url'), 
            InlineKeyboardButton('✗ 𝖢𝗁𝖺𝗇𝗀𝖾 𝖠𝖯𝖨', callback_data='change_short_api')
        ],
        [
            InlineKeyboardButton('✗ 𝖱𝖾𝗌𝖾𝗍 𝖲𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋', callback_data='reset_shortener')
        ],
        [
            InlineKeyboardButton('✗ 𝖡𝖺𝖼𝗄 𝗍𝗈 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌', callback_data='settings')
        ]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

# This handler is triggered when the "𝗌𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋" button is clicked in the main settings
@Client.on_callback_query(filters.regex("^shortner_settings$"))
async def shortner_settings_callback(client: Client, query: CallbackQuery):
    if not (query.from_user.id == client.owner):
        return await query.answer('✗ 𝖮𝗇𝗅𝗒 𝗍𝗁𝖾 𝖻𝗈𝗍 𝗈𝗐𝗇𝖾𝗋 𝖼𝖺𝗇 𝖺𝖼𝖼𝖾𝗌𝗌 𝗍𝗁𝗂𝗌 𝗆𝖾𝗇𝗎.', show_alert=True)
    await shortner_settings_main(client, query)

# This handler changes the URL
@Client.on_callback_query(filters.regex("^change_short_url$"))
async def change_short_url(client: Client, query: CallbackQuery):
    await query.answer()
    
    current_url = f"**𝖢𝗎𝗋𝗋𝖾𝗇𝗍:** `{client.short_url}`" if client.short_url else "**𝖢𝗎𝗋𝗋𝖾𝗇𝗍:** 𝖭𝗈𝗍 𝖲𝖾𝗍"
    
    try:
        ask_msg = await client.ask(
            chat_id=query.from_user.id,
            text=f"""**𝖴𝗉𝖽𝖺𝗍𝖾 𝖲𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋 𝖴𝖱𝖫**

{current_url}

**𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝗇𝖾𝗐 𝗌𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋 𝖴𝖱𝖫:**
• 𝖤𝗑𝖺𝗆𝗉𝗅𝖾: `𝗒𝗈𝗎𝗋.𝖽𝗈𝗆𝖺𝗂𝗇.𝖼𝗈𝗆`
• 𝖤𝗑𝖺𝗆𝗉𝗅𝖾: `𝖺𝗉𝗂.𝗌𝗁𝗈𝗋𝗍𝖾𝗇.𝗂𝗈`

**✗ 𝖳𝗒𝗉𝖾** `𝖼𝖺𝗇𝖼𝖾𝗅` **𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.**""",
            filters=filters.text, 
            timeout=120
        )
        
        if ask_msg.text.lower() == 'cancel':
            await ask_msg.reply("**❌ 𝖮𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽.**")
        else:
            new_url = ask_msg.text.strip()
            client.short_url = new_url
            # Save the new setting to the database
            await client.mongodb.save_settings(client.session_name, client.get_current_settings())
            
            await ask_msg.reply(f"""**✅ 𝖲𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋 𝖴𝖱𝖫 𝖴𝗉𝖽𝖺𝗍𝖾𝖽**

**🌐 𝖭𝖾𝗐 𝖴𝖱𝖫:** `{new_url}`
**📊 𝖲𝗍𝖺𝗍𝗎𝗌:** 𝖠𝖼𝗍𝗂𝗏𝖾 𝖺𝗇𝖽 𝗌𝖺𝗏𝖾𝖽""")
            
    except ListenerTimeout:
        await query.message.reply("**⏰ 𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖮𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽.**")
    
    # Refresh the shortener settings menu
    await shortner_settings_main(client, query)

# This handler changes the API key
@Client.on_callback_query(filters.regex("^change_short_api$"))
async def change_short_api(client: Client, query: CallbackQuery):
    await query.answer()
    
    current_status = "**𝖢𝗎𝗋𝗋𝖾𝗇𝗍:** 𝖠𝖯𝖨 𝖪𝖾𝗒 𝖲𝖾𝗍 ✓" if client.short_api else "**𝖢𝗎𝗋𝗋𝖾𝗇𝗍:** 𝖭𝗈 𝖠𝖯𝖨 𝖪𝖾𝗒 ❌"
    
    try:
        ask_msg = await client.ask(
            chat_id=query.from_user.id,
            text=f"""**🥂 𝖴𝗉𝖽𝖺𝗍𝖾 𝖲𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋 𝖠𝖯𝖨 𝖪𝖾𝗒**

{current_status}

**📥 𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝗇𝖾𝗐 𝗌𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋 𝖠𝖯𝖨 𝖪𝖾𝗒:**
• 𝖸𝗈𝗎𝗋 𝖠𝖯𝖨 𝗄𝖾𝗒 𝗐𝗂𝗅𝗅 𝖻𝖾 𝗌𝖾𝖼𝗎𝗋𝖾𝗅𝗒 𝗌𝗍𝗈𝗋𝖾𝖽
• 𝖬𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗂𝗍'𝗌 𝖼𝗈𝗋𝗋𝖾𝖼𝗍 𝖿𝗈𝗋 𝗒𝗈𝗎𝗋 𝖽𝗈𝗆𝖺𝗂𝗇

**❌ 𝖳𝗒𝗉𝖾** `𝖼𝖺𝗇𝖼𝖾𝗅` **𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.**""",
            filters=filters.text, 
            timeout=120
        )
        
        if ask_msg.text.lower() == 'cancel':
            await ask_msg.reply("**❌ 𝖮𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽.**")
        else:
            new_api = ask_msg.text.strip()
            client.short_api = new_api
            # Save the new setting to the database
            await client.mongodb.save_settings(client.session_name, client.get_current_settings())
            
            await ask_msg.reply(f"""**✅ 𝖠𝖯𝖨 𝖪𝖾𝗒 𝖴𝗉𝖽𝖺𝗍𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒**

**🔐 𝖲𝗍𝖺𝗍𝗎𝗌:** 𝖠𝖯𝖨 𝖪𝖾𝗒 𝖲𝖺𝗏𝖾𝖽
**📊 𝖲𝖾𝖼𝗎𝗋𝗂𝗍𝗒:** 𝖪𝖾𝗒 𝗂𝗌 𝗆𝖺𝗌𝗄𝖾𝖽 𝖿𝗈𝗋 𝗌𝖾𝖼𝗎𝗋𝗂𝗍𝗒
**💾 𝖲𝗍𝗈𝗋𝖺𝗀𝖾:** 𝖲𝖾𝖼𝗎𝗋𝖾𝗅𝗒 𝗌𝖺𝗏𝖾𝖽 𝗍𝗈 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾""")
            
    except ListenerTimeout:
        await query.message.reply("**⏰ 𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖮𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽.**")

    # Refresh the shortener settings menu
    await shortner_settings_main(client, query)

# New handler to reset shortener settings
@Client.on_callback_query(filters.regex("^reset_shortener$"))
async def reset_shortener(client: Client, query: CallbackQuery):
    await query.answer()
    
    confirmation_text = """**🔄 𝖱𝖾𝗌𝖾𝗍 𝖲𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌**

**⚠️ 𝖠𝗋𝖾 𝗒𝗈𝗎 𝗌𝗎𝗋𝖾 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗋𝖾𝗌𝖾𝗍?**
**𝖳𝗁𝗂𝗌 𝗐𝗂𝗅𝗅 𝖼𝗅𝖾𝖺𝗋 𝖻𝗈𝗍𝗁 𝖴𝖱𝖫 𝖺𝗇𝖽 𝖠𝖯𝖨 𝖪𝖾𝗒.**

**📝 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌:**
• **𝖴𝖱𝖫:** `{url}`
• **𝖠𝖯𝖨:** `{api_status}`"""

    current_url = client.short_url if client.short_url else "𝖭𝗈𝗍 𝖲𝖾𝗍"
    api_status = "𝖲𝖾𝗍" if client.short_api else "𝖭𝗈𝗍 𝖲𝖾𝗍"
    
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('✓ 𝖸𝖾𝗌, 𝖱𝖾𝗌𝖾𝗍', callback_data='confirm_reset_shortener'),
            InlineKeyboardButton('✗ 𝖢𝖺𝗇𝖼𝖾𝗅', callback_data='shortner_settings')
        ]
    ])
    
    await query.message.edit_text(
        confirmation_text.format(url=current_url, api_status=api_status),
        reply_markup=reply_markup
    )

# Handler for confirming reset
@Client.on_callback_query(filters.regex("^confirm_reset_shortener$"))
async def confirm_reset_shortener(client: Client, query: CallbackQuery):
    await query.answer()
    
    # Store old values for confirmation message
    old_url = client.short_url
    old_api_status = "𝖲𝖾𝗍" if client.short_api else "𝖭𝗈𝗍 𝖲𝖾𝗍"
    
    # Reset the values
    client.short_url = None
    client.short_api = None
    
    # Save to database
    await client.mongodb.save_settings(client.session_name, client.get_current_settings())
    
    success_msg = f"""**𝖲𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌 𝖱𝖾𝗌𝖾𝗍**

**✗ 𝖯𝗋𝖾𝗏𝗂𝗈𝗎𝗌 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌 𝖢𝗅𝖾𝖺𝗋𝖾𝖽:**
• **𝖴𝖱𝖫:** `{old_url or "𝖭𝗈𝗍 𝖲𝖾𝗍"}`
• **𝖠𝖯𝖨 𝖪𝖾𝗒:** {old_api_status}

**𝖲𝗁𝗈𝗋𝗍𝖾𝗇𝖾𝗋 𝗂𝗌 𝗇𝗈𝗐 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽.**
**𝖲𝖾𝗍 𝗇𝖾𝗐 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌 𝗍𝗈 𝖾𝗇𝖺𝖻𝗅𝖾 𝖺𝗀𝖺𝗂𝗇.**"""
    
    await query.message.edit_text(success_msg)
    
    # Return to shortener settings after a delay
    await asyncio.sleep(2)
    await shortner_settings_main(client, query)
