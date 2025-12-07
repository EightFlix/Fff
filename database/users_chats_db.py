from motor.motor_asyncio import AsyncIOMotorClient # Changed to motor
from info import (
    BOT_ID, ADMINS, DATABASE_NAME, DATA_DATABASE_URL, FILES_DATABASE_URL, 
    SECOND_FILES_DATABASE_URL, IMDB_TEMPLATE, WELCOME_TEXT, LINK_MODE, 
    TUTORIAL, SHORTLINK_URL, SHORTLINK_API, SHORTLINK, FILE_CAPTION, 
    IMDB, WELCOME, SPELL_CHECK, PROTECT_CONTENT, AUTO_DELETE, 
    IS_STREAM, VERIFY_EXPIRE
)
import time
# timedelta को इम्पोर्ट किया गया
from datetime import datetime, timedelta 

# MongoClient को AsyncIOMotorClient से बदला गया (यदि motor का उपयोग कर रहे हैं)
files_db_client = AsyncIOMotorClient(FILES_DATABASE_URL)
files_db = files_db_client[DATABASE_NAME]

data_db_client = AsyncIOMotorClient(DATA_DATABASE_URL)
data_db = data_db_client[DATABASE_NAME]

if SECOND_FILES_DATABASE_URL:
     second_files_db_client = AsyncIOMotorClient(SECOND_FILES_DATABASE_URL)
     second_files_db = second_files_db_client[DATABASE_NAME]

class Database:
    # ... (default_setgs, default_verify, default_prm आर ठीक)

    def __init__(self):
        self.col = data_db.Users
        self.grp = data_db.Groups
        self.prm = data_db.Premiums
        self.req = data_db.Requests
        self.con = data_db.Connections
        self.stg = data_db.Settings
        # ... (rest of __init__ is fine)

    # Note: If motor is used, await must be added to all database calls. 
    # The following are changed to reflect motor usage (assuming all methods use await):
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user) # AWAIT added

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)}) # AWAIT added
        return bool(user)

    async def total_users_count(self):
        # AWAIT added
        count = await self.col.count_documents({}) 
        return count
    
    # ... (other similar methods like ban_user, remove_ban, add_chat need await added to DB calls)
    
    # ... (del_join_req, find_join_req, add_join_req are simple and fine)
    
    async def get_verify_status(self, user_id):
        user = await self.col.find_one({'id':int(user_id)})
        if user:
            info = user.get('verify_status', self.default_verify)
            
            # 3. get_verify_status fix: using timedelta and correct dict update
            if 'expire_time' not in info or info['expire_time'] == 0:
                # Assuming verified_time is a datetime object or timestamp 
                # If verified_time is not set, use current time
                base_time = info.get('verified_time') or datetime.now()
                info['expire_time'] = base_time + timedelta(seconds=VERIFY_EXPIRE)
                
            return info
        return self.default_verify
        
    async def update_verify_status(self, user_id, verify):
        await self.col.update_one({'id': int(user_id)}, {'$set': {'verify_status': verify}})
    
    # ... (get_files_db_size, get_second_files_db_size, get_data_db_size need AWAIT)
    
    # Changed to async for consistency with other methods and motor usage
    async def get_plan(self, id):
        st = await self.prm.find_one({'id': id})
        if st:
            return st['status']
        return self.default_prm
    
    # Changed to async for consistency and motor usage
    async def update_plan(self, id, data):
        if not await self.prm.find_one({'id': id}):
            await self.prm.insert_one({'id': id, 'status': data})
        await self.prm.update_one({'id': id}, {'$set': {'status': data}})

    # Changed to async and filter added for clarity
    async def get_premium_users(self):
        # Only return active premium users
        return self.prm.find({'status.premium': True}) 
    
    # ... (get_connections, update_bot_sttgs, get_bot_sttgs are fine, assuming AWAIT is added to DB calls)
