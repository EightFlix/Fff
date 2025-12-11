import logging
import asyncio
from time import time
from hydrogram import Client, filters, enums
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from hydrogram.errors import FloodWait, MessageDeleteForbidden
from utils import is_check_admin, save_group_settings, temp

logger = logging.getLogger(__name__)

# --- 🛡️ MANAGE PANEL (UI IMPROVED) ---
@Client.on_message(filters.command('manage') & filters.group)
async def manage_panel(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("<b>❌ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ!</b>\n\nʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ.")
        
    btn = [
        [
            InlineKeyboardButton('🔇 Uɴᴍᴜᴛᴇ Aʟʟ', callback_data=f'mng_unmute#{message.chat.id}'),
            InlineKeyboardButton('🗑️ Cʟᴇᴀɴ Dᴇʟᴇᴛᴇᴅ', callback_data=f'mng_kick_del#{message.chat.id}')
        ],
        [
            InlineKeyboardButton('⚙️ Gʀᴏᴜᴘ Sᴇᴛᴛɪɴɢs', callback_data=f'open_group_settings')
        ],
        [
            InlineKeyboardButton('❌ Cʟᴏsᴇ', callback_data='close_data')
        ]
    ]
    
    await message.reply_text(
        f"<b>🛡️ <u>Gʀᴏᴜᴘ Cᴏᴍᴍᴀɴᴅᴇʀ</u></b>\n\n"
        f"<b>🏷️ Gʀᴏᴜᴘ:</b> {message.chat.title}\n"
        f"<b>🆔 ID:</b> <code>{message.chat.id}</code>\n\n"
        f"<i>Sᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴛɪᴏɴ ғʀᴏᴍ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴛʜɪs ɢʀᴏᴜᴘ.</i>", 
        reply_markup=InlineKeyboardMarkup(btn)
    )

# --- 🗑️ PURGE COMMAND (NEW FEATURE) ---
@Client.on_message(filters.command("purge") & filters.group)
async def purge_func(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to start purging from there.</b>")

    msg = await message.reply("<b>🗑️ Pᴜʀɢɪɴɢ Sᴛᴀʀᴛᴇᴅ...</b>")
    
    message_ids = []
    count = 0
    # Collect messages from reply to current
    for msg_id in range(message.reply_to_message.id, message.id + 1):
        message_ids.append(msg_id)
        if len(message_ids) == 100:
            try:
                await client.delete_messages(message.chat.id, message_ids)
                count += len(message_ids)
                message_ids = []
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                pass
    
    # Delete remaining
    if message_ids:
        try:
            await client.delete_messages(message.chat.id, message_ids)
            count += len(message_ids)
        except: pass

    # Success Message
    done = await message.reply(f"<b>✅ Sᴜᴄᴄᴇssғᴜʟʟʏ Pᴜʀɢᴇᴅ {count} Mᴇssᴀɢᴇs!</b>")
    await asyncio.sleep(3)
    await done.delete()

# --- 📌 PIN COMMAND (NEW FEATURE) ---
@Client.on_message(filters.command("pin") & filters.group)
async def pin_func(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    
    try:
        await message.reply_to_message.pin(disable_notification=True)
        await message.reply("<b>📌 Mᴇssᴀɢᴇ Pɪɴɴᴇᴅ!</b>")
    except Exception as e:
        await message.reply(f"Error: {e}")

# --- 🔊 ACTION CALLBACKS ---
@Client.on_callback_query(filters.regex(r"^mng_"))
async def manage_callbacks(client, query):
    _, action, chat_id = query.data.split("#")
    chat_id = int(chat_id)
    
    if not await is_check_admin(client, chat_id, query.from_user.id):
        return await query.answer("🛑 You are not an Admin!", show_alert=True)

    if action == "unmute":
        await query.message.edit("<b>🔊 Uɴᴍᴜᴛɪɴɢ Eᴠᴇʀʏᴏɴᴇ... Pʟᴇᴀsᴇ Wᴀɪᴛ.</b>")
        unmuted = 0
        try:
            async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.RESTRICTED):
                if not member.permissions.can_send_messages:
                    try:
                        await client.unban_chat_member(chat_id, member.user.id)
                        unmuted += 1
                        await asyncio.sleep(0.1) # Avoid flood
                    except: pass
            
            await query.message.edit(f"<b>✅ Oᴘᴇʀᴀᴛɪᴏɴ Cᴏᴍᴘʟᴇᴛᴇ!</b>\n\n🔊 Uɴᴍᴜᴛᴇᴅ: {unmuted} Mᴇᴍʙᴇʀs.")
        except Exception as e:
            await query.message.edit(f"❌ Error: {e}")

    elif action == "kick_del":
        await query.message.edit("<b>🧟 Sᴄᴀɴɴɪɴɢ ғᴏʀ Zᴏᴍʙɪᴇ (Dᴇʟᴇᴛᴇᴅ) Aᴄᴄᴏᴜɴᴛs...</b>")
        kicked = 0
        try:
            async for member in client.get_chat_members(chat_id):
                if member.user.is_deleted:
                    try:
                        await client.ban_chat_member(chat_id, member.user.id)
                        await client.unban_chat_member(chat_id, member.user.id) # Unban immediately to just kick
                        kicked += 1
                        await asyncio.sleep(0.1)
                    except: pass
            
            await query.message.edit(f"<b>✅ Cʟᴇᴀɴᴜᴘ Cᴏᴍᴘʟᴇᴛᴇ!</b>\n\n🧟 Kɪᴄᴋᴇᴅ: {kicked} Zᴏᴍʙɪᴇs.")
        except Exception as e:
            await query.message.edit(f"❌ Error: {e}")

# --- ⚙️ SETTINGS LISTENERS ---
@Client.on_callback_query(filters.regex(r"^(caption_setgs|welcome_setgs|tutorial_setgs)"))
async def settings_callbacks(client, query):
    action, group_id = query.data.split("#")
    group_id = int(group_id)
    
    if not await is_check_admin(client, group_id, query.from_user.id):
        return await query.answer("🚫 You are not an Admin!", show_alert=True)
    
    mapping = {
        "caption_setgs": ("caption", "📝 <b>Sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ Fɪʟᴇ Cᴀᴘᴛɪᴏɴ:</b>\n\n<i>Use {file_name} and {file_size} as variables.</i>"),
        "welcome_setgs": ("welcome_text", "👋 <b>Sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ Wᴇʟᴄᴏᴍᴇ Mᴇssᴀɢᴇ:</b>\n\n<i>Use {mention} for user link.</i>"),
        "tutorial_setgs": ("tutorial", "🎥 <b>Sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ Tᴜᴛᴏʀɪᴀʟ Lɪɴᴋ:</b>")
    }
    
    db_key, text_prompt = mapping[action]
    
    await query.message.delete()
    try:
        ask_msg = await client.send_message(query.message.chat.id, text_prompt)
    except:
        return
        
    try:
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id, timeout=60)
        if msg.text:
            await save_group_settings(group_id, db_key, msg.text)
            success = await client.send_message(query.message.chat.id, f"<b>✅ Sᴇᴛᴛɪɴɢs Uᴘᴅᴀᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!</b>")
            await asyncio.sleep(3)
            await success.delete()
        else:
            await client.send_message(query.message.chat.id, "❌ Iɴᴠᴀʟɪᴅ Iɴᴘᴜᴛ. Pʀᴏᴄᴇss Cᴀɴᴄᴇʟʟᴇᴅ.")
    except Exception:
        await client.send_message(query.message.chat.id, "⏳ Tɪᴍᴇᴏᴜᴛ. Pʀᴏᴄᴇss Cᴀɴᴄᴇʟʟᴇᴅ.")
    finally:
        try: await ask_msg.delete()
        except: pass
