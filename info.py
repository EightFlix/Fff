import re
from os import environ
import os
from Script import script
import logging

logger = logging.getLogger(__name__)

def is_enabled(type, value):
    # ... (यह फ़ंक्शन वही रहेगा, यह उत्कृष्ट है)
    data = environ.get(type, str(value))
    if data.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif data.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        logger.error(f'{type} is invalid, exiting now')
        exit()

def is_valid_ip(ip):
    # ... (यह फ़ंक्शन वही रहेगा, यह उत्कृष्ट है)
    ip_pattern = r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    return re.match(ip_pattern, ip) is not None

# Bot information
API_ID = environ.get('API_ID', '')
if not API_ID.isdigit(): # API_ID की बेहतर जाँच
    logger.error('API_ID is missing or invalid, exiting now')
    exit()
API_ID = int(API_ID)
    
API_HASH = environ.get('API_HASH', '')
if len(API_HASH) == 0:
    logger.error('API_HASH is missing, exiting now')
    exit()
    
BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    logger.error('BOT_TOKEN is missing, exiting now')
    exit()
    
try:
    BOT_ID = int(BOT_TOKEN.split(":")[0])
except ValueError:
    logger.error('BOT_TOKEN is invalid (BOT_ID part is not an integer), exiting now')
    exit()

PORT = int(environ.get('PORT', '80'))

# Random images
PICS = environ.get('PICS', 'https://i.postimg.cc/8C15CQ5y/1.png').split()

# Bot Admins
ADMINS_STR = environ.get('ADMINS', '')
if len(ADMINS_STR) == 0:
    logger.error('ADMINS is missing, exiting now')
    exit()
try:
    ADMINS = [int(admins) for admins in ADMINS_STR.split()]
except ValueError:
    logger.error('ADMINS must contain only integer IDs separated by space, exiting now')
    exit()

# Channels
# यह जाँच करता है कि क्या यह एक ID है (यानी -100 या 12345), यदि हाँ तो int में बदलें।
INDEX_CHANNELS = [int(ch) if ch.lstrip('-').isdigit() else ch for ch in environ.get('INDEX_CHANNELS', '').split()]
if len(INDEX_CHANNELS) == 0:
    logger.info('INDEX_CHANNELS is empty')
    
LOG_CHANNEL_STR = environ.get('LOG_CHANNEL', '')
if not LOG_CHANNEL_STR.lstrip('-').isdigit():
    logger.error('LOG_CHANNEL is missing or invalid, exiting now')
    exit()
LOG_CHANNEL = int(LOG_CHANNEL_STR)
    
# support group
SUPPORT_GROUP_STR = environ.get('SUPPORT_GROUP', '')
if not SUPPORT_GROUP_STR.lstrip('-').isdigit():
    logger.error('SUPPORT_GROUP is missing or invalid, exiting now')
    exit()
SUPPORT_GROUP = int(SUPPORT_GROUP_STR)

# MongoDB information
DATA_DATABASE_URL = environ.get('DATA_DATABASE_URL', "")
if not DATA_DATABASE_URL.startswith('mongodb'):
    logger.error('DATA_DATABASE_URL must start with mongodb, exiting now')
    exit()
    
FILES_DATABASE_URL = environ.get('FILES_DATABASE_URL', "")
if not FILES_DATABASE_URL.startswith('mongodb'):
    logger.error('FILES_DATABASE_URL must start with mongodb, exiting now')
    exit()

SECOND_FILES_DATABASE_URL = environ.get('SECOND_FILES_DATABASE_URL', "")
if len(SECOND_FILES_DATABASE_URL) == 0:
    logger.info('SECOND_FILES_DATABASE_URL is empty')

DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Files')

# ... (बाकी वैरिएबल्स ठीक हैं)
