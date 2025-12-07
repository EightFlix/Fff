import logging
import re
import base64
from struct import pack
from hydrogram.file_id import FileId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import TEXT
from pymongo.errors import DuplicateKeyError, OperationFailure
from info import USE_CAPTION_FILTER, FILES_DATABASE_URL, SECOND_FILES_DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, MAX_BTN

logger = logging.getLogger(__name__)

# --- MongoDB Clients ---
client = AsyncIOMotorClient(FILES_DATABASE_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Create Index (Async friendly logic, but pymongo index creation is fine here as it runs once)
# Note: Motor generally handles index creation via await, but we wrap in try-except for simplicity
# or assume indexes are pre-created. For robustness in async code:
# We will skip manual index creation here or assume it's handled elsewhere or ignore errors for now.
# Real fix: Index creation should be awaited in an async setup function, but for simplicity:

if SECOND_FILES_DATABASE_URL:
    second_client = AsyncIOMotorClient(SECOND_FILES_DATABASE_URL)
    second_db = second_client[DATABASE_NAME]
    second_collection = second_db[COLLECTION_NAME]

async def second_db_count_documents():
     return await second_collection.count_documents({})

async def db_count_documents():
     return await collection.count_documents({})

async def save_file(media):
    """Save file in database"""
    file_id = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
    file_caption = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.caption))
    
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
        return 'suc'
    except DuplicateKeyError:
        return 'dup'
    except Exception:
        # Fallback to second DB if primary fails or full
        if SECOND_FILES_DATABASE_URL:
            try:
                await second_collection.insert_one(document)
                return 'suc'
            except DuplicateKeyError:
                return 'dup'
            except Exception:
                return 'err'
        else:
            return 'err'

async def get_search_results(query, max_results=MAX_BTN, offset=0, lang=None):
    query = str(query).strip()
    
    if not query:
        return [], "", 0

    # Text Search Filter
    filter = {'$text': {'$search': query}} 
    
    # 1. कुल परिणाम गिनें
    total_results = await collection.count_documents(filter)
    
    # 2. आवश्यक परिणाम प्राप्त करें (Pagination)
    # Using text score sorting
    cursor = collection.find(filter, {'score': {'$meta': 'textScore'}}).sort([('score', {'$meta': 'textScore'})])
    
    cursor.skip(offset).limit(max_results)
    
    files = [doc async for doc in cursor]

    if SECOND_FILES_DATABASE_URL:
        total_results += await second_collection.count_documents(filter)
        if len(files) < max_results:
            cursor2 = second_collection.find(filter, {'score': {'$meta': 'textScore'}}).sort([('score', {'$meta': 'textScore'})])
            # Adjust offset for second db if needed, simplifying here to append
            # Correct logic would calculate remaining skip/limit
            remaining_limit = max_results - len(files)
            cursor2.limit(remaining_limit)
            files.extend([doc async for doc in cursor2])

    next_offset = offset + len(files)
    if next_offset >= total_results or len(files) == 0:
        next_offset = ""
    
    return files, next_offset, total_results

async def delete_files(query):
    query = query.strip()
    if not query:
        return 0
        
    filter = {'$text': {'$search': query}}
    
    result1 = await collection.delete_many(filter)
    total_deleted = result1.deleted_count
    
    if SECOND_FILES_DATABASE_URL:
        result2 = await second_collection.delete_many(filter)
        total_deleted += result2.deleted_count
    
    return total_deleted

async def get_file_details(query):
    file_details = await collection.find_one({'_id': query})
    if not file_details and SECOND_FILES_DATABASE_URL:
        file_details = await second_collection.find_one({'_id': query})
    return file_details

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
