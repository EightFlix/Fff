import logging
from hydrogram import Client, filters, enums
from info import ADMINS

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("id"))
async def show_id(client, message):
    """Get Chat ID and User ID with Emojis"""
    chat = message.chat
    your_id = message.from_user.id if message.from_user else 0
    reply = message.reply_to_message

    # Header
    text = f"<b>🆔 <u>Iᴅᴇɴᴛɪᴛʏ Iɴғᴏʀᴍᴀᴛɪᴏɴ</u></b>\n\n"
    
    # Chat Info
    text += f"<b>💬 Cʜᴀᴛ Iᴅ:</b> <code>{chat.id}</code>\n"
    if chat.username:
        text += f"<b>🔗 Cʜᴀᴛ Uɴᴀᴍᴇ:</b> @{chat.username}\n"
    
    # User Info
    text += f"<b>👤 Yᴏᴜʀ Iᴅ:</b> <code>{your_id}</code>\n"

    # Reply Info
    if reply:
        text += f"\n<b>🔄 Rᴇᴘʟɪᴇᴅ Mᴇssᴀɢᴇ:</b>\n"
        text += f" • <b>👤 Usᴇʀ Iᴅ:</b> <code>{reply.from_user.id}</code>\n"
        if reply.forward_from_chat:
            text += f" • <b>⏩ Fᴏʀᴡᴀʀᴅ Cʜᴀɴɴᴇʟ:</b> <code>{reply.forward_from_chat.id}</code>\n"
        
    await message.reply(text, quote=True)

@Client.on_message(filters.command("info"))
async def show_info(client, message):
    """Get User Info like an ID Card (Including DC ID)"""
    if not message.reply_to_message:
        user = message.from_user
    else:
        user = message.reply_to_message.from_user
    
    if not user:
        return await message.reply("<b>❌ Cᴏᴜʟᴅ ɴᴏᴛ ғɪɴᴅ ᴜsᴇʀ ɪɴғᴏ!</b>")

    # Format Data
    username = f"@{user.username}" if user.username else "None"
    is_bot = "Yes 🤖" if user.is_bot else "No 👤"
    dc_id = f"{user.dc_id}" if user.dc_id else "Unknown" # DC ID added here
    
    # Beautified Text
    text = (
        f"<b>🪪 <u>Usᴇʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ</u></b>\n\n"
        f"<b>👤 Nᴀᴍᴇ:</b> {user.first_name}\n"
        f"<b>🆔 Iᴅ:</b> <code>{user.id}</code>\n"
        f"<b>📛 Usᴇʀɴᴀᴍᴇ:</b> {username}\n"
        f"<b>🌐 Dᴀᴛᴀ Cᴇɴᴛᴇʀ:</b> {dc_id}\n"
        f"<b>🔗 Pʀᴏғɪʟᴇ:</b> {user.mention}\n"
        f"<b>🤖 Is Bᴏᴛ:</b> {is_bot}\n"
    )
    await message.reply(text, quote=True)

@Client.on_message(filters.command("json") & filters.user(ADMINS))
async def show_json(client, message):
    """Get Raw JSON (Admin Only)"""
    target_msg = message.reply_to_message or message
    
    try:
        await message.reply(
            f"<b>⚙️ <u>Rᴀᴡ Mᴇssᴀɢᴇ Dᴀᴛᴀ</u></b>\n\n<code>{target_msg}</code>",
            quote=True
        )
    except Exception as e:
        await message.reply(f"<b>❌ Eʀʀᴏʀ:</b> {e}")
