import asyncio
import re
import math
import urllib.parse
from info import (
    ADMINS, MAX_BTN, IS_STREAM, DELETE_TIME, LOG_CHANNEL, SUPPORT_GROUP, QUALITY
)
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from hydrogram import Client, filters, enums
from hydrogram.errors import MessageNotModified
from utils import (
    is_premium, get_size, is_check_admin, temp, get_settings
)
from database.ia_filterdb import get_search_results

# =====================================================
# MEMORY CACHE (ULTRA FAST)
# =====================================================
BUTTONS = {}
SEARCH_CACHE = {}
CACHE_TTL = 180  # 3 minutes

# Pre-compiled regex for performance
EXT_PATTERN = re.compile(r"\b(mkv|mp4|avi|m4v|webm|flv|mov|wmv|3gp|mpg|mpeg)\b", re.IGNORECASE)
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+|t\.me/\S+|@\w+')

# =====================================================
# FAST CACHE FUNCTIONS
# =====================================================
def get_cache(key):
    """Get cached search results"""
    if key in SEARCH_CACHE:
        data, timestamp = SEARCH_CACHE[key]
        import time
        if time.time() - timestamp < CACHE_TTL:
            return data
        SEARCH_CACHE.pop(key, None)
    return None

def set_cache(key, value):
    """Cache search results"""
    import time
    SEARCH_CACHE[key] = (value, time.time())
    # Limit cache size
    if len(SEARCH_CACHE) > 500:
        oldest = min(SEARCH_CACHE.items(), key=lambda x: x[1][1])
        SEARCH_CACHE.pop(oldest[0], None)

# =====================================================
# OPTIMIZED FILE LINK BUILDER
# =====================================================
def build_file_links(files, chat_id, start_index=1):
    """Build file links in bulk (fast)"""
    links = []
    for index, file in enumerate(files, start=start_index):
        f_name = EXT_PATTERN.sub("", file.get('file_name', 'Unknown'))
        f_name = ' '.join(f_name.split()).title().replace(" L ", " l ")
        size = get_size(file.get('file_size', 0))
        file_id = file.get('_id', '')
        link = f"https://t.me/{temp.U_NAME}?start=file_{chat_id}_{file_id}"
        links.append(f"{index}. <a href='{link}'>[{size}] {f_name}</a>")
    return "\n\n<b>".join([""] + links) if links else ""

# =====================================================
# PM SEARCH (PREMIUM ONLY)
# =====================================================
@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_search(client, message):
    # Ignore commands
    if message.text.startswith("/"):
        return
    
    # Premium check
    if not await is_premium(message.from_user.id, client):
        return
    
    # Quick search indicator (no edit needed later)
    asyncio.create_task(handle_search(client, message, is_pm=True))

# =====================================================
# GROUP SEARCH
# =====================================================
@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_search(client, message):
    # Support group link deletion
    try:
        if SUPPORT_GROUP:
            support_id = int(SUPPORT_GROUP[0] if isinstance(SUPPORT_GROUP, list) else SUPPORT_GROUP)
            if message.chat.id == support_id and URL_PATTERN.search(message.text):
                asyncio.create_task(delete_after_delay(message, 300))
                return
    except:
        pass
    
    # Premium check
    if not await is_premium(message.from_user.id, client):
        return
    
    # Ignore commands
    if message.text.startswith("/"):
        return
    
    # Admin mentions
    if '@admin' in message.text.lower():
        if await is_check_admin(client, message.chat.id, message.from_user.id):
            return
        return
    
    # Link detection
    if URL_PATTERN.search(message.text):
        if await is_check_admin(client, message.chat.id, message.from_user.id):
            return
        try:
            await message.delete()
        except:
            pass
        return await message.reply('<b>⚠️ Links are not allowed here!</b>')
    
    # Request handling
    if '#request' in message.text.lower():
        if message.from_user.id not in ADMINS:
            await client.send_message(
                LOG_CHANNEL,
                f"#Request\nUser: {message.from_user.mention}\nMsg: {message.text}"
            )
            await message.reply_text("<b>✅ Request Sent Successfully!</b>")
            return
    
    # Handle search (non-blocking)
    asyncio.create_task(handle_search(client, message, is_pm=False))

# =====================================================
# UNIFIED FAST SEARCH HANDLER
# =====================================================
async def handle_search(client, message, is_pm):
    """Ultra-fast unified search handler"""
    try:
        # Prepare search query (fast regex)
        search = ' '.join(message.text.replace("-", " ").replace(":", " ").split()).strip()
        
        # Check cache first
        cache_key = f"{search}:0"
        cached = get_cache(cache_key)
        
        if cached:
            files, offset, total = cached
        else:
            # Send "searching" only if no cache
            status = await message.reply("🔍 Searching...")
            
            # Fetch from database
            files, offset, total = await get_search_results(search, max_results=MAX_BTN)
            
            # Cache results
            set_cache(cache_key, (files, offset, total))
            
            # Delete status message
            try:
                await status.delete()
            except:
                pass
        
        # No results
        if not files:
            google_url = f"https://www.google.com/search?q={urllib.parse.quote(search)}"
            btn = [[InlineKeyboardButton("🔍 Check Google", url=google_url)]]
            await message.reply(
                f'<b>❌ No Results Found:</b> <code>{search}</code>',
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return
        
        # Store in temp
        req = message.from_user.id
        key = f"{message.chat.id}-{message.id}"
        temp.FILES[key] = files
        BUTTONS[key] = search
        
        # Build message
        files_link = build_file_links(files, message.chat.id)
        
        # Buttons
        btn = [[
            InlineKeyboardButton("♻️ Send All", url=f"https://t.me/{temp.U_NAME}?start=all_{message.chat.id}_{key}"),
            InlineKeyboardButton("⚙️ Quality", callback_data=f"quality#{key}#{req}#0")
        ]]
        
        if offset:
            btn.append([
                InlineKeyboardButton(f"🗓 1/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
                InlineKeyboardButton("Next ⏩", callback_data=f"next_{req}_{key}_{offset}")
            ])
        
        # Caption
        cap = (
            f"<b>✨ Search Results</b>\n\n"
            f"<b>🔍 Query:</b> <i>{search}</i>\n"
            f"<b>📂 Total:</b> {total}\n"
            f"{files_link}"
        )
        
        # Get settings for auto-delete
        settings = await get_settings(message.chat.id)
        
        # Send result
        result = await message.reply(cap, reply_markup=InlineKeyboardMarkup(btn))
        
        # Auto-delete if enabled
        if settings.get("auto_delete"):
            asyncio.create_task(auto_delete_result(result, message, DELETE_TIME, btn, req, key, offset))
    
    except Exception as e:
        print(f"Search error: {e}")
        try:
            await message.reply("❌ Search error occurred")
        except:
            pass

# =====================================================
# FAST PAGINATION
# =====================================================
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    try:
        _, req, key, offset = query.data.split("_")
        
        # Owner check
        if int(req) != query.from_user.id and query.from_user.id not in ADMINS:
            return await query.answer("🛑 Not your result!", show_alert=True)
        
        # Get search term
        search = BUTTONS.get(key)
        if not search:
            return await query.answer("❌ Session Expired!", show_alert=True)
        
        offset = int(offset)
        
        # Check cache
        cache_key = f"{search}:{offset}"
        cached = get_cache(cache_key)
        
        if cached:
            files, n_offset, total = cached
        else:
            # Fetch from DB
            files, n_offset, total = await get_search_results(search, offset=offset, max_results=MAX_BTN)
            set_cache(cache_key, (files, n_offset, total))
        
        if not files:
            return await query.answer("No more results")
        
        # Build links
        files_link = build_file_links(files, query.message.chat.id, offset + 1)
        
        # Navigation buttons
        btn = [[
            InlineKeyboardButton("♻️ Send All", url=f"https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}"),
            InlineKeyboardButton("⚙️ Quality", callback_data=f"quality#{key}#{req}#{offset}")
        ]]
        
        nav = []
        if offset > 0:
            back_offset = max(0, offset - MAX_BTN)
            nav.append(InlineKeyboardButton("⏪ Back", callback_data=f"next_{req}_{key}_{back_offset}"))
        
        nav.append(InlineKeyboardButton(
            f"🗓 {math.ceil(offset / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}",
            callback_data="buttons"
        ))
        
        if n_offset:
            nav.append(InlineKeyboardButton("Next ⏩", callback_data=f"next_{req}_{key}_{n_offset}"))
        
        btn.append(nav)
        
        # Update message
        cap = (
            f"<b>✨ Search Results</b>\n\n"
            f"<b>🔍 Query:</b> <i>{search}</i>\n"
            f"<b>📂 Total:</b> {total}\n"
            f"{files_link}"
        )
        
        await query.message.edit_text(cap, reply_markup=InlineKeyboardMarkup(btn))
        await query.answer()
    
    except MessageNotModified:
        await query.answer()
    except Exception as e:
        print(f"Pagination error: {e}")
        await query.answer("Error occurred")

# =====================================================
# QUALITY FILTER
# =====================================================
@Client.on_callback_query(filters.regex(r"^quality"))
async def quality(client, query):
    try:
        _, key, req, offset = query.data.split("#")
        
        if int(req) != query.from_user.id:
            return await query.answer("🛑 Not your result!", show_alert=True)
        
        btn = []
        for i in range(0, len(QUALITY), 3):
            row = [
                InlineKeyboardButton(
                    QUALITY[i+j].upper(),
                    callback_data=f"qual_search#{QUALITY[i+j]}#{key}#{offset}#{req}"
                )
                for j in range(3) if i + j < len(QUALITY)
            ]
            btn.append(row)
        
        btn.append([InlineKeyboardButton("⪻ Back", callback_data=f"next_{req}_{key}_{offset}")])
        
        await query.message.edit_text(
            "<b>🔽 Select Quality:</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        await query.answer()
    except Exception as e:
        await query.answer("Error")

# =====================================================
# AUTO DELETE WITH RESTORE
# =====================================================
async def auto_delete_result(result_msg, original_msg, delay, btn, req, key, offset):
    """Auto-delete search results with restore option"""
    try:
        await asyncio.sleep(delay)
        
        # Delete both messages
        try:
            await result_msg.delete()
            await original_msg.delete()
        except:
            pass
        
        # Send restore button
        restore_btn = [[
            InlineKeyboardButton(
                "♻️ Get Files Again",
                callback_data=f"next_{req}_{key}_{offset if offset else 0}"
            )
        ]]
        
        gone_msg = await original_msg.reply(
            "<b>🗑️ Files Deleted!</b>\n\nClick below to retrieve.",
            reply_markup=InlineKeyboardMarkup(restore_btn)
        )
        
        # Delete restore message after 12 hours
        await asyncio.sleep(43200)
        try:
            await gone_msg.delete()
        except:
            pass
    except:
        pass

# =====================================================
# HELPER: DELETE AFTER DELAY
# =====================================================
async def delete_after_delay(message, delay):
    """Delete message after delay"""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass
