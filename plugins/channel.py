import logging
from hydrogram import Client, filters, enums
from info import INDEX_CHANNELS
from database.ia_filterdb import save_file
from database.users_chats_db import db

logger = logging.getLogger(__name__)

@Client.on_message(filters.channel & filters.incoming)
async def index_handler(bot, message):
    # 1. Check Media (अगर मीडिया नहीं है तो इग्नोर करें)
    if not message.media:
        return 

    # 2. Chat ID Check करें
    chat_id = message.chat.id
    
    # 3. Check Permissions (Database या Config में ID है या नहीं)
    is_indexed = False
    if chat_id in INDEX_CHANNELS:
        is_indexed = True
    else:
        try:
            db_channels = await db.get_index_channels_db()
            if chat_id in db_channels:
                is_indexed = True
        except:
            pass

    # अगर ID मैच नहीं हुई, तो लॉग में चेतावनी दें (ताकि आपको पता चले)
    if not is_indexed:
        logger.warning(f"⚠️ Ignored Channel ID: {chat_id} (Not in Index List)")
        return

    # 4. Media Extract करें
    try:
        media = getattr(message, message.media.value)
    except:
        return

    # 5. Junk Filter (2MB से छोटी फाइल इग्नोर)
    if media.file_size < 2 * 1024 * 1024:
        return 

    # 6. Save to DB
    media.file_type = message.media.value
    media.caption = message.caption

    try:
        sts = await save_file(media)
        
        if sts == 'suc':
            # सफलता पर ❤️
            try: await message.react(emoji="💖")
            except: pass
            logger.info(f"✅ Indexed: {getattr(media, 'file_name', 'Unknown')}")
            
        elif sts == 'dup':
            # डुप्लीकेट पर 🦄
            try: await message.react(emoji="🦄")
            except: pass
            logger.info(f"♻️ Duplicate Found: {getattr(media, 'file_name', 'Unknown')}")
            
        elif sts == 'err':
            logger.error(f"❌ Error Saving File")
            
    except Exception as e:
        logger.error(f"Channel Index Error: {e}")

@Client.on_edited_message(filters.channel)
async def edit_handler(bot, message):
    if not message.media: return
    # Edit handler logic same as above (omitted for brevity but ensure ID check)
    if message.chat.id not in INDEX_CHANNELS:
        return
    
    media = getattr(message, message.media.value)
    media.file_type = message.media.value
    media.caption = message.caption
    
    await save_file(media)
    try: await message.react(emoji="✍️")
    except: pass
