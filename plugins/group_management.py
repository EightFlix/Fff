import logging
from hydrogram import Client, filters, enums
from utils import is_check_admin
from hydrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

@Client.on_message(filters.command('manage') & filters.group)
async def members_management(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
        
    btn = [[
        InlineKeyboardButton('Unmute All', callback_data='unmute_all_members'),
        InlineKeyboardButton('Unban All', callback_data='unban_all_members')
    ],[
        InlineKeyboardButton('Kick Muted Users', callback_data='kick_muted_members'),
        InlineKeyboardButton('Kick Deleted Accounts', callback_data='kick_deleted_accounts_members')
    ]]
    await message.reply_text("Select one of function to manage members.", reply_markup=InlineKeyboardMarkup(btn))


@Client.on_message(filters.command('ban') & filters.group)
async def ban_chat_user(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
        
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            user_id = message.command[1]
            if user_id.isdigit():
                user_id = int(user_id)
            # यदि username है तो string ही रहने दें
        except IndexError:
            return await message.reply_text("Reply to any user message or give user id, username")
    else:
        return await message.reply_text("Reply to a user or provide username/ID to ban.")

    try:
        # यूजर की जानकारी प्राप्त करें (नाम दिखाने के लिए)
        member = await client.get_chat_member(message.chat.id, user_id)
        user = member.user
    except Exception:
        # यदि यूजर ग्रुप में नहीं है, तो भी हम ID से बैन करने का प्रयास कर सकते हैं
        # लेकिन mention के लिए user object नहीं मिलेगा
        user = None

    try:
        # FIX: message.from_user.id को message.chat.id से बदला गया
        await client.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
        
        mention = user.mention if user else f"User ID: {user_id}"
        await message.reply_text(f'Successfully banned {mention} from {message.chat.title}')
    except Exception as e:
        logger.error(f"Ban Error: {e}")
        return await message.reply_text("I can't ban this user. Make sure I am Admin with Ban rights and the user is not an Admin.")


@Client.on_message(filters.command('mute') & filters.group)
async def mute_chat_user(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
        
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            user_id = message.command[1]
            if user_id.isdigit():
                user_id = int(user_id)
        except IndexError:
            pass
            
    if not user_id:
         return await message.reply_text("Reply to a user or provide username/ID to mute.")

    try:
        member = await client.get_chat_member(message.chat.id, user_id)
        user = member.user
    except Exception:
        return await message.reply_text("Can't find the given user in this group.")

    try:
        # ChatPermissions() सभी अनुमतियों को प्रतिबंधित (Restrict) कर देगा (Mute)
        await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
        await message.reply_text(f'Successfully muted {user.mention} from {message.chat.title}')
    except Exception as e:
        logger.error(f"Mute Error: {e}")
        return await message.reply_text("I don't have access to mute user. Check my permissions.")


@Client.on_message(filters.command(["unban", "unmute"]) & filters.group)
async def unban_chat_user(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
        
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            user_id = message.command[1]
            if user_id.isdigit():
                user_id = int(user_id)
        except IndexError:
            pass
            
    if not user_id:
        return await message.reply_text("Reply to any user message or give user id, username")

    try:
        # अनबैन करने से पहले यूजर की जानकारी लेने की कोशिश (ऑप्शनल)
        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            user_mention = member.user.mention
        except:
            user_mention = f"User ({user_id})"

        # Unban और Unmute दोनों के लिए unban_chat_member काम करता है (यह किक नहीं करता, बस प्रतिबंध हटाता है)
        await client.unban_chat_member(message.chat.id, user_id)
        
        command_type = "unmuted" if "unmute" in message.command[0] else "unbanned"
        await message.reply_text(f'Successfully {command_type} {user_mention} from {message.chat.title}')
        
    except Exception as e:
        logger.error(f"Unban/Unmute Error: {e}")
        return await message.reply_text(f"I don't have access to {message.command[0]} user. Check my permissions.")
