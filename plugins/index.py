import re
import time
import asyncio
import logging
from hydrogram import Client, filters, enums
from hydrogram.errors import FloodWait
from info import ADMINS
from database.ia_filterdb import save_file
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp, get_readable_time

logger = logging.getLogger(__name__)
lock = asyncio.Lock()

# --- Custom Iterator Logic ---
async def iter_messages(bot, chat_id, limit, offset):
    """
    Custom generator to iterate through messages by ID.
    Fetches messages in batches of 200 for speed.
    """
    current = offset
    while current < limit:
        new_diff = min(200, limit - current)
        if new_diff <= 0:
            return
        
        batch_ids = list(range(current, current + new_diff + 1))
        
        try:
            messages = await bot.get_messages(chat_id, batch_ids)
            for message in messages:
                if message:
                    yield message
                    
        except FloodWait as e:
            await asyncio.sleep(e.value)
            continue
        except Exception as e:
            logger.error(f"Error fetching batch {current}: {e}")
            pass
            
        current += 200

# --- CALLBACK QUERY HANDLER ---

@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    _, ident, chat, lst_msg_id, skip = query.data.split("#")
    
    if query.from_user.id not in ADMINS:
         return await query.answer("You are not authorized to use this.", show_alert=True)
         
    if ident == 'yes':
        msg = query.message
        await msg.edit("Starting Indexing...")
        try:
            chat = int(chat)
        except ValueError:
            pass
        await index_files_to_db(int(lst_msg_id), chat, msg, bot, int(skip))
    elif ident == 'cancel':
        temp.CANCEL = True
        await query.message.edit("Trying to cancel Indexing...")


# --- INITIATION HANDLER ---

@Client.on_message(filters.forwarded & filters.private & filters.incoming & filters.user(ADMINS))
async def send_for_index(bot, message):
    if lock.locked():
        return await message.reply('Wait until previous process complete.')
        
    msg = message
    chat_id = None
    last_msg_id = None
    
    if msg.text and msg.text.startswith("https://t.me"):
        try:
            msg_link = msg.text.split("/")
            last_msg_id = int(msg_link[-1])
            chat_id = msg_link[-2]
            if chat_id.isnumeric():
                chat_id = int(("-100" + chat_id)) 
        except Exception as e:
            logger.error(f"Link parsing error: {e}")
            await message.reply('Invalid message link!')
            return
            
    elif msg.forward_from_chat and msg.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = msg.forward_from_message_id
        chat_id = msg.forward_from_chat.username or msg.forward_from_chat.id
    else:
        await message.reply('This is not a forwarded message or link.')
        return
        
    try:
        chat = await bot.get_chat(chat_id)
    except Exception as e:
        return await message.reply(f'Errors - {e}')

    if chat.type != enums.ChatType.CHANNEL:
        return await message.reply("I can index only channels.")

    s = await message.reply("Send skip message number.")
    try:
        msg_skip = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id, timeout=30) 
        await s.delete()
        skip = int(msg_skip.text)
    except Exception:
        await s.delete()
        return await message.reply("Number is invalid or timeout.")
        
    buttons = [[
        InlineKeyboardButton('YES', callback_data=f'index#yes#{chat_id}#{last_msg_id}#{skip}')
    ],[
        InlineKeyboardButton('CLOSE', callback_data='close_data'),
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply(f'Do you want to index {chat.title} channel?\nTotal Messages: <code>{last_msg_id}</code>', reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)


# --- INDEXING CORE LOGIC ---

async def index_files_to_db(lst_msg_id, chat, msg, bot, skip):
    start_time = time.time()
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    
    current = skip
    
    async with lock:
        try:
            async for message in iter_messages(bot, chat, lst_msg_id, skip):
                time_taken = get_readable_time(time.time()-start_time)
                
                if temp.CANCEL:
                    temp.CANCEL = False
                    await msg.edit_text(f"Successfully Cancelled!\nCompleted in {time_taken}\n\nSaved <code>{total_files}</code> files to Database!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>\nUnsupported Media: <code>{unsupported}</code>\nErrors Occurred: <code>{errors}</code>", parse_mode=enums.ParseMode.HTML)
                    return
                    
                current += 1
                
                if current % 100 == 0:
                    btn = [[
                        InlineKeyboardButton('CANCEL', callback_data=f'index#cancel#{chat}#{lst_msg_id}#{skip}')
                    ]]
                    try:
                        await msg.edit_text(text=f"Total messages received: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>\nUnsupported Media: <code>{unsupported}</code>\nErrors Occurred: <code>{errors}</code>", reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                    except Exception:
                        pass
                        
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                
                # Check for Video, Document, Audio
                elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT, enums.MessageMediaType.AUDIO]:
                    unsupported += 1
                    continue
                
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                
                # Set Type and Caption
                media.file_type = message.media.value
                media.caption = message.caption
                
                # NOTE: File Name Cleaning removed from here as it is now handled in ia_filterdb.py
                
                sts = await save_file(media) 
                
                if sts == 'suc':
                    total_files += 1
                elif sts == 'dup':
                    duplicate += 1
                elif sts == 'err':
                    errors += 1
                    
        except Exception as e:
            logger.error(f"Indexing failed for chat {chat}: {e}")
            await msg.reply(f'Index canceled due to Error - {e}')
            
        else:
            time_taken = get_readable_time(time.time()-start_time)
            await msg.edit_text(f'Succesfully saved <code>{total_files}</code> to Database!\nCompleted in {time_taken}\n\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>\nUnsupported Media: <code>{unsupported}</code>\nErrors Occurred: <code>{errors}</code>', parse_mode=enums.ParseMode.HTML)
