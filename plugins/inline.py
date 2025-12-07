import logging
from hydrogram import Client
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from database.ia_filterdb import get_search_results
from utils import get_size, temp, get_verify_status, is_subscribed, is_premium
from info import CACHE_TIME, SUPPORT_LINK, UPDATES_LINK, FILE_CAPTION, IS_VERIFY

# लॉगिंग सेट करें
logger = logging.getLogger(__name__)
cache_time = CACHE_TIME

def is_banned(query: InlineQuery):
    return query.from_user and query.from_user.id in temp.BANNED_USERS

@Client.on_inline_query()
async def inline_search(bot, query):
    """Show search results for given inline query"""
    try:
        # 1. Force Subscribe Check
        # is_subscribed आमतौर पर बटन की लिस्ट देता है अगर यूजर ने ज्वाइन नहीं किया है
        fsub_buttons = await is_subscribed(bot, query) 
        if fsub_buttons:
            await query.answer(
                results=[],
                cache_time=0,
                switch_pm_text="⚠️ Join Updates Channel First",
                switch_pm_parameter="inline_fsub"
            )
            return

        # 2. Ban Check
        if is_banned(query):
            await query.answer(
                results=[],
                cache_time=0,
                switch_pm_text="🚫 You are Banned!",
                switch_pm_parameter="start"
            )
            return

        # 3. Verification Check
        verify_status = await get_verify_status(query.from_user.id)
        if IS_VERIFY and not verify_status['is_verified'] and not await is_premium(query.from_user.id, bot):
            await query.answer(
                results=[],
                cache_time=0,
                switch_pm_text="🔐 Verify to Search",
                switch_pm_parameter="inline_verify"
            )
            return

        # 4. Search Logic
        string = query.query.strip()
        offset = int(query.offset or 0)
        
        # सर्च रिजल्ट्स प्राप्त करें
        files, next_offset, total = await get_search_results(string, offset=offset)

        results = []
        for file in files:
            reply_markup = get_reply_markup(string)
            
            # सुरक्षित कैप्शन फ़ॉर्मेटिंग
            caption_template = file.get('caption') or ""
            f_caption = FILE_CAPTION.format(
                file_name=file.get('file_name', ''),
                file_size=get_size(file.get('file_size', 0)),
                caption=caption_template
            )
            
            results.append(
                InlineQueryResultCachedDocument(
                    title=file.get('file_name', 'Unknown File'),
                    document_file_id=file['_id'],
                    caption=f_caption,
                    description=f'Size: {get_size(file.get("file_size", 0))}',
                    reply_markup=reply_markup
                )
            )

        # 5. परिणाम भेजें
        if results:
            switch_pm_text = f"📂 {total} Results Found"
            if string:
                switch_pm_text += f' for: {string}'
            
            await query.answer(
                results=results,
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text[:64], # Telegram limit 64 chars
                switch_pm_parameter="start",
                next_offset=str(next_offset)
            )
        else:
            switch_pm_text = '❌ No Results Found'
            if string:
                switch_pm_text += f' for: {string}'
            
            await query.answer(
                results=[],
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text[:64],
                switch_pm_parameter="start"
            )

    except Exception as e:
        logger.error(f"Inline Search Error: {e}")
        # यूजर को पता न चले कि एरर आया है, बस खाली रिजल्ट भेजें ताकि लोड होना बंद हो जाए
        await query.answer(results=[], switch_pm_text="Error occurred", switch_pm_parameter="start")


def get_reply_markup(s):
    buttons = [[
        InlineKeyboardButton('🔎 Search Again', switch_inline_query_current_chat=s or '')
    ],[
        InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ⚡️', url=UPDATES_LINK),
        InlineKeyboardButton('💡 Support Group 💡', url=SUPPORT_LINK)
    ]]
    return InlineKeyboardMarkup(buttons)
