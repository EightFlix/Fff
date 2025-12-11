import logging
import re
import base64
from struct import pack
from hydrogram.file_id import FileId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import TEXT
from pymongo.errors import DuplicateKeyError
from info import DATA_DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, MAX_BTN, USE_CAPTION_FILTER

logger = logging.getLogger(__name__)

# --- Single Database Connection ---
client = AsyncIOMotorClient(DATA_DATABASE_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# --- ⚡ COMPILED REGEX PATTERNS (For High Performance) ---
RE_SPECIAL = re.compile(r"[\.\+\-_]")
RE_USERNAMES = re.compile(r"@\w+")
RE_BRACKETS = re.compile(r"[\[\(\{].*?[\]\}\)]")
RE_EXTENSIONS = re.compile(r"\b(mkv|mp4|avi|m4v|webm|flv)\b", flags=re.IGNORECASE)
RE_SPACES = re.compile(r"\s+")

async def save_file(media):
    """
    Save file with Optimized Cleaning & Emoji Logging.
    """
    file_id = unpack_new_file_id(media.file_id)
    
    # --- FILENAME CLEANING ---
    original_name = str(media.file_name or "")
    
    # Apply Compiled Regex (Faster)
    clean_name = RE_SPECIAL.sub(" ", original_name)
    clean_name = RE_USERNAMES.sub("", clean_name)
    clean_name = RE_BRACKETS.sub("", clean_name)
    clean_name = RE_EXTENSIONS.sub("", clean_name)
    clean_name = RE_SPACES.sub(" ", clean_name)
    
    file_name = clean_name.strip().lower()
    
    # --- CAPTION CLEANING ---
    original_caption = str(media.caption or "")
    
    clean_caption = RE_SPECIAL.sub(" ", original_caption)
    clean_caption = RE_USERNAMES.sub("", clean_caption)
    clean_caption = RE_BRACKETS.sub("", clean_caption)
    clean_caption = RE_EXTENSIONS.sub("", clean_caption)
    clean_caption = RE_SPACES.sub(" ", clean_caption)
    
    file_caption = clean_caption.strip().lower()
    
    document = {
        '_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size,
        'caption': file_caption,
        'file_type': media.file_type,
        'mime_type': media.mime_type
    }
    
    try:
        await collection.insert_one(document)
        # Advanced Logging
        logger.info(f"✅ Saved: {file_name[:50]}...") 
        return 'suc'
    except DuplicateKeyError:
        # logger.info(f"♻️ Duplicate: {file_name[:50]}...") # Uncomment if you want logs for dupes
        return 'dup'
    except Exception as e:
        logger.error(f"❌ Error Saving: {e}")
        return 'err'

async def get_search_results(query, max_results=MAX_BTN, offset=0, lang=None):
    """
    Hybrid Search:
    Layer 1: MongoDB Text Search (Fast & Accurate)
    Layer 2: Regex Split Search (Smart Fallback + Caption Support)
    """
    
    # Cleaning the query
    query = str(query).strip().lower()
    query = RE_SPECIAL.sub(" ", query)
    query = RE_SPACES.sub(" ", query).strip()

    if not query:
        return [], "", 0

    # --- LAYER 1: Text Search (Standard) ---
    if lang:
        search_query = f'"{query}" "{lang}"' 
        filter_dict = {'$text': {'$search': search_query}}
    else:
        filter_dict = {'$text': {'$search': query}} 
    
    try:
        total_results = await collection.count_documents(filter_dict)
        
        if total_results > 0:
            cursor = collection.find(filter_dict, {'score': {'$meta': 'textScore'}}).sort([('score', {'$meta': 'textScore'})])
            cursor.skip(offset).limit(max_results)
            files = [doc async for doc in cursor]
            
            next_offset = offset + len(files)
            if next_offset >= total_results or len(files) == 0:
                next_offset = ""
            return files, next_offset, total_results

        # --- LAYER 2: Smart Regex Search (Fallback + Caption Filter) ---
        if offset == 0:
            words = query.split()
            if len(words) > 0: 
                regex_pattern = ""
                for word in words:
                    regex_pattern += f"(?=.*{re.escape(word)})"
                
                # Check USE_CAPTION_FILTER from Info
                if USE_CAPTION_FILTER:
                    regex_filter = {
                        '$or': [
                            {'file_name': {'$regex': regex_pattern, '$options': 'i'}},
                            {'caption': {'$regex': regex_pattern, '$options': 'i'}}
                        ]
                    }
                else:
                    regex_filter = {'file_name': {'$regex': regex_pattern, '$options': 'i'}}
                
                total_results_regex = await collection.count_documents(regex_filter)
                
                if total_results_regex > 0:
                    cursor = collection.find(regex_filter).sort('_id', -1)
                    cursor.limit(max_results)
                    files = [doc async for doc in cursor]
                    return files, "", total_results_regex

        return [], "", 0
        
    except Exception as e:
        logger.error(f"❌ Search Error: {e}")
        return [], "", 0

async def get_file_details(query):
    try:
        file_details = await collection.find_one({'_id': query})
        return file_details
    except Exception:
        return None

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id

async def db_count_documents():
     return await collection.count_documents({})

async def second_db_count_documents():
     return 0

async def delete_files(query):
    query = query.strip()
    if not query: return 0
    filter = {'$text': {'$search': query}}
    result1 = await collection.delete_many(filter)
    logger.info(f"🗑️ Deleted {result1.deleted_count} files for query: {query}")
    return result1.deleted_count
