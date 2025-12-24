import logging
import re
import base64
import asyncio
from struct import pack
from typing import List, Tuple, Optional
from hydrogram.file_id import FileId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import TEXT, DESCENDING
from pymongo.errors import DuplicateKeyError, OperationFailure
from info import DATA_DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, MAX_BTN, USE_CAPTION_FILTER

logger = logging.getLogger(__name__)

# =====================================================
# DATABASE CONNECTION WITH POOLING
# =====================================================
client = AsyncIOMotorClient(
    DATA_DATABASE_URL,
    maxPoolSize=50,  # Connection pool for performance
    minPoolSize=10,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000
)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# =====================================================
# PRE-COMPILED REGEX PATTERNS (PERFORMANCE BOOST)
# =====================================================
RE_SPECIAL = re.compile(r"[\.\+\-_]")
RE_USERNAMES = re.compile(r"@\w+")
RE_BRACKETS = re.compile(r"[\[\(\{].*?[\]\}\)]")
RE_EXTENSIONS = re.compile(r"\b(mkv|mp4|avi|m4v|webm|flv)\b", re.IGNORECASE)
RE_SPACES = re.compile(r"\s+")

# =====================================================
# IN-MEMORY CACHE (ULTRA FAST)
# =====================================================
SEARCH_CACHE = {}
CACHE_TTL = 180  # 3 minutes
MAX_CACHE_SIZE = 1000

def get_cache(key: str) -> Optional[Tuple]:
    """Get cached search results"""
    if key in SEARCH_CACHE:
        import time
        data, timestamp = SEARCH_CACHE[key]
        if time.time() - timestamp < CACHE_TTL:
            return data
        SEARCH_CACHE.pop(key, None)
    return None

def set_cache(key: str, value: Tuple):
    """Cache search results with size limit"""
    import time
    SEARCH_CACHE[key] = (value, time.time())
    
    # Prevent memory overflow
    if len(SEARCH_CACHE) > MAX_CACHE_SIZE:
        oldest = min(SEARCH_CACHE.items(), key=lambda x: x[1][1])
        SEARCH_CACHE.pop(oldest[0], None)

# =====================================================
# CREATE INDEXES (ONE-TIME SETUP)
# =====================================================
async def create_indexes():
    """Create necessary indexes for fast search"""
    try:
        # Text search index
        await collection.create_index(
            [("file_name", TEXT), ("caption", TEXT)],
            name="file_search_index"
        )
        
        # Regular index for sorting
        await collection.create_index([("_id", DESCENDING)])
        
        logger.info("✅ Indexes created successfully")
    except Exception as e:
        logger.warning(f"Index creation: {e}")

# =====================================================
# FAST TEXT CLEANER
# =====================================================
def clean_text(text: str) -> str:
    """Ultra-fast text cleaning"""
    if not text:
        return ""
    
    # Apply all regex in one pass
    text = RE_SPECIAL.sub(" ", text)
    text = RE_USERNAMES.sub("", text)
    text = RE_BRACKETS.sub("", text)
    text = RE_EXTENSIONS.sub("", text)
    text = RE_SPACES.sub(" ", text)
    
    # Title case with specific replacements
    return text.strip().title().replace(" L ", " l ")

# =====================================================
# SAVE FILE (OPTIMIZED)
# =====================================================
async def save_file(media) -> str:
    """Save file with minimal processing"""
    try:
        file_id = unpack_new_file_id(media.file_id)
        
        # Fast cleaning
        file_name = clean_text(str(media.file_name or ""))
        file_caption = clean_text(str(media.caption or ""))
        
        document = {
            '_id': file_id,
            'file_name': file_name,
            'file_size': media.file_size,
            'caption': file_caption,
            'file_type': media.file_type,
            'mime_type': media.mime_type
        }
        
        await collection.insert_one(document)
        return 'suc'
    
    except DuplicateKeyError:
        return 'dup'
    except Exception as e:
        logger.error(f"Save error: {e}")
        return 'err'

# =====================================================
# UPDATE FILE (OPTIMIZED)
# =====================================================
async def update_file(media) -> str:
    """Update file with minimal processing"""
    try:
        file_id = unpack_new_file_id(media.file_id)
        
        file_name = clean_text(str(media.file_name or ""))
        file_caption = clean_text(str(media.caption or ""))
        
        await collection.update_one(
            {'_id': file_id},
            {'$set': {
                'file_name': file_name,
                'caption': file_caption,
                'file_size': media.file_size
            }}
        )
        return 'suc'
    except Exception as e:
        logger.error(f"Update error: {e}")
        return 'err'

# =====================================================
# ULTRA-FAST SEARCH (WITH CACHING)
# =====================================================
async def get_search_results(
    query: str,
    max_results: int = MAX_BTN,
    offset: int = 0,
    lang: Optional[str] = None
) -> Tuple[List, any, int]:
    """Ultra-fast search with caching and optimization"""
    
    # Validate input
    if not query or len(query.strip()) < 2:
        return [], "", 0
    
    # Clean query
    query = query.strip().lower()
    query = RE_SPECIAL.sub(" ", query)
    query = RE_SPACES.sub(" ", query).strip()
    
    # Check cache first
    cache_key = f"{query}:{offset}:{lang}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    # ================================================
    # METHOD 1: TEXT SEARCH (FASTEST)
    # ================================================
    try:
        # Build search query
        if lang:
            search_query = f'"{query}" "{lang}"'
        else:
            search_query = query
        
        filter_dict = {'$text': {'$search': search_query}}
        
        # Count total (with limit for performance)
        total = await collection.count_documents(filter_dict, limit=10000)
        
        if total > 0:
            # Fetch results with projection (faster)
            cursor = collection.find(
                filter_dict,
                {
                    'file_name': 1,
                    'file_size': 1,
                    'caption': 1,
                    'score': {'$meta': 'textScore'}
                }
            ).sort([('score', {'$meta': 'textScore'})])
            
            # Apply pagination
            cursor.skip(offset).limit(max_results)
            
            # Convert to list efficiently
            results = await cursor.to_list(length=max_results)
            
            # Calculate next offset
            next_offset = offset + len(results)
            if next_offset >= total or len(results) < max_results:
                next_offset = ""
            
            # Cache and return
            result = (results, next_offset, total)
            set_cache(cache_key, result)
            return result
    
    except OperationFailure:
        pass  # Fall through to regex
    except Exception as e:
        logger.error(f"Text search error: {e}")
    
    # ================================================
    # METHOD 2: REGEX SEARCH (FALLBACK)
    # ================================================
    try:
        words = query.split()
        if not words:
            return [], "", 0
        
        # Build optimized regex pattern
        # Instead of (?=.*word1)(?=.*word2), use direct pattern
        if len(words) == 1:
            pattern = re.escape(words[0])
        else:
            # Match all words in any order
            pattern = ".*".join([re.escape(word) for word in words])
        
        # Build filter
        if USE_CAPTION_FILTER:
            regex_filter = {
                '$or': [
                    {'file_name': {'$regex': pattern, '$options': 'i'}},
                    {'caption': {'$regex': pattern, '$options': 'i'}}
                ]
            }
        else:
            regex_filter = {'file_name': {'$regex': pattern, '$options': 'i'}}
        
        # Count with limit
        total = await collection.count_documents(regex_filter, limit=5000)
        
        if total > 0:
            # Fetch with projection
            cursor = collection.find(
                regex_filter,
                {'file_name': 1, 'file_size': 1, 'caption': 1}
            ).sort('_id', DESCENDING)
            
            cursor.skip(offset).limit(max_results)
            results = await cursor.to_list(length=max_results)
            
            # Calculate next offset
            next_offset = offset + len(results)
            if next_offset >= total or len(results) < max_results:
                next_offset = ""
            
            # Cache and return
            result = (results, next_offset, min(total, 5000))
            set_cache(cache_key, result)
            return result
    
    except Exception as e:
        logger.error(f"Regex search error: {e}")
    
    return [], "", 0

# =====================================================
# GET FILE DETAILS (CACHED)
# =====================================================
FILE_CACHE = {}
FILE_CACHE_TTL = 300  # 5 minutes

async def get_file_details(file_id: str) -> Optional[dict]:
    """Get file details with caching"""
    if not file_id:
        return None
    
    # Check cache
    if file_id in FILE_CACHE:
        import time
        data, timestamp = FILE_CACHE[file_id]
        if time.time() - timestamp < FILE_CACHE_TTL:
            return data
        FILE_CACHE.pop(file_id, None)
    
    # Fetch from DB
    try:
        file_data = await collection.find_one({'_id': file_id})
        
        # Cache result
        if file_data:
            import time
            FILE_CACHE[file_id] = (file_data, time.time())
        
        return file_data
    except Exception as e:
        logger.error(f"Get file error: {e}")
        return None

# =====================================================
# FILE ID ENCODING (NO CHANGES NEEDED)
# =====================================================
def encode_file_id(s: bytes) -> str:
    """Encode file ID to base64"""
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

def unpack_new_file_id(new_file_id: str) -> str:
    """Decode and unpack Telegram file ID"""
    try:
        decoded = FileId.decode(new_file_id)
        return encode_file_id(
            pack(
                "<iiqq",
                int(decoded.file_type),
                decoded.dc_id,
                decoded.media_id,
                decoded.access_hash
            )
        )
    except Exception as e:
        logger.error(f"Unpack file ID error: {e}")
        return ""

# =====================================================
# DATABASE COUNT (FAST)
# =====================================================
async def db_count_documents() -> int:
    """Get approximate document count (fast)"""
    try:
        return await collection.estimated_document_count()
    except:
        return 0

# =====================================================
# DELETE FILES (OPTIMIZED)
# =====================================================
async def delete_files(query: str) -> int:
    """Delete files matching query"""
    try:
        # Delete all
        if not query or query.strip() == "":
            result = await collection.delete_many({})
            
            # Clear caches
            SEARCH_CACHE.clear()
            FILE_CACHE.clear()
            
            logger.info(f"🗑️ Deleted all files: {result.deleted_count}")
            return result.deleted_count
        
        # Delete specific
        query = query.strip()
        filter_dict = {'file_name': {'$regex': query, '$options': 'i'}}
        
        result = await collection.delete_many(filter_dict)
        
        # Clear caches
        SEARCH_CACHE.clear()
        FILE_CACHE.clear()
        
        logger.info(f"🗑️ Deleted {result.deleted_count} files")
        return result.deleted_count
    
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return 0

# =====================================================
# STARTUP INITIALIZATION
# =====================================================
async def init_database():
    """Initialize database on startup"""
    try:
        await create_indexes()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"Database init error: {e}")

# Run initialization
asyncio.create_task(init_database())
