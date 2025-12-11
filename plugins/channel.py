import logging
from hydrogram import Client, filters
from info import INDEX_CHANNELS
from database.ia_filterdb import save_file
from database.users_chats_db import db

logger = logging.getLogger(__name__)

@Client.on_message(filters.channel & filters.incoming)
async def debug_and_index(bot, message):
    """
    1. Logs EVERY message from ANY channel the bot is in.
    2. Checks if that channel is in your Config or DB.
    3. Saves file if matched.
    """
    
    # 1. Get Real Chat ID
    chat_id = message.chat.id
    chat_name = message.chat.title
    
    # --- DEBUG LOG (ये कंसोल में दिखाएगा कि बोट किस चैनल को देख रहा है) ---
    # अगर ये लॉग नहीं आ रहा, तो बोट चैनल में एडमिन सही से नहीं बना है।
    # logger.info(f"👀 Detected Message in: {chat_name} | ID: {chat_id}")

    # 2. Check Database & Config
    is_indexed = False
    
    # Check Config (info.py)
    if chat_id in INDEX_CHANNELS:
        is_indexed = True
        # logger.info(f"✅ Config Match found for {chat_id}")
    else:
        # Check Database
        try:
            db_channels = await db.get_index_channels_db()
            if chat_id in db_channels:
                is_indexed = True
                # logger.info(f"✅ DB Match found for {chat_id}")
        except:
            pass

    # अगर चैनल मैच नहीं हुआ, तो रिटर्न (इग्नोर) करें
    if not is_indexed:
        # (Optional) अनकमेंट करें अगर आप देखना चाहते हैं कि कौन से चैनल इग्नोर हो रहे हैं
        # logger.warning(f"❌ Channel {chat_id} is NOT in Index List. Ignoring.")
        return

    # 3. Check for Media
    if not message.media:
        return

    # 4. Media Handling
    try:
        media = getattr(message, message.media.value, None)
    except Exception:
        media = None
        
    if not media:
        return

    # --- Junk Filter ---
    if media.file_size < 2 * 1024 * 1024: # 2MB
        try: await message.react(emoji="🗑️")
        except: pass
        return

    media.file_type = message.media.value
    media.caption = message.caption

    # 5. Save to DB
    try:
        sts = await save_file(media)
        
        if sts == 'suc':
            try: await message.react(emoji="💖")
            except: pass
            logger.info(f"✅ Auto Indexed: {getattr(media, 'file_name', 'Unknown')} | Channel: {chat_id}")
            
        elif sts == 'dup':
            try: await message.react(emoji="🦄")
            except: pass
            
        elif sts == 'err':
            try: await message.react(emoji="💔")
            except: pass
            logger.error(f"❌ Error Saving File")
            
    except Exception as e:
        logger.error(f"Handler Error: {e}")

@Client.on_edited_message(filters.channel)
async def edit_handler(bot, message):
    # Same logic for Edits
    chat_id = message.chat.id
    if chat_id not in INDEX_CHANNELS:
        try:
            db_channels = await db.get_index_channels_db()
            if chat_id not in db_channels:
                return
        except: return

    if not message.media: return
    try: media = getattr(message, message.media.value)
    except: return
    
    if media.file_size < 2 * 1024 * 1024: return

    media.file_type = message.media.value
    media.caption = message.caption
    
    await save_file(media)
    try: await message.react(emoji="✍️")
    except: pass
