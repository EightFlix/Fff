import sys
import glob
import importlib
from pathlib import Path
from hydrogram import Client, idle
import logging
import logging.config
import asyncio
from aiohttp import web
from time import time
from datetime import datetime, timezone
import pytz

# Local Imports
from info import API_ID, API_HASH, BOT_TOKEN, PORT, LOG_CHANNEL, TIME_ZONE
from utils import temp
from Script import script
from web import web_app
from database.users_chats_db import db
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("hydrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="FastFinderBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=10,
        )

    async def start(self):
        # Set Start Time
        temp.START_TIME = time()
        
        # Set Bot Instance for Web Server
        temp.BOT = self 
        
        # Start Client
        await super().start()
        me = await self.get_me()
        
        # Set Temp Variables
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        temp.B_ID = me.id
        
        # Start Web Server (For Streaming)
        app = web.AppRunner(web_app)
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()
        logging.info(f"Web Server Started on Port {PORT}")
        
        logging.info(f"@{me.username} Started Successfully! 🚀")
        
        # Start Premium Expiry Checker Loop
        self.loop.create_task(self.check_premium_expiry())

        # Send Startup Log
        if LOG_CHANNEL:
            try:
                await self.send_message(
                    chat_id=LOG_CHANNEL,
                    text=f"<b>🚀 {me.mention} Is Online!</b>\n\n<b>📅 Date:</b> <code>{time()}</code>"
                )
            except Exception as e:
                logging.error(f"Failed to send log: {e}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped. Bye!")

    # --- PREMIUM EXPIRY CHECKER TASK (FIXED) ---
    async def check_premium_expiry(self):
        logging.info("Premium Expiry Checker Started...")
        while True:
            try:
                # Iterate through all users in Premium Collection
                async for user in await db.get_premium_users():
                    try:
                        user_id = user['id']
                        plan_status = user.get('status', {})
                        expiry_date = plan_status.get('expire')
                        
                        # Skip if not premium or no expiry date
                        if not plan_status.get('premium') or not isinstance(expiry_date, datetime):
                            continue
                        
                        # --- FIX: Ensure expiry_date is offset-aware ---
                        if expiry_date.tzinfo is None:
                            expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                        # -----------------------------------------------

                        # Calculate remaining time in seconds
                        now = datetime.now(timezone.utc)
                        delta = expiry_date - now
                        seconds = delta.total_seconds()
                        
                        # Format Expiry Time (e.g. 10/12/2025 08:30 PM)
                        try:
                            tz = pytz.timezone(TIME_ZONE)
                            expiry_ist = expiry_date.astimezone(tz)
                            expiry_str = expiry_ist.strftime("%d/%m/%Y %I:%M %p")
                        except:
                            expiry_str = expiry_date.strftime("%d/%m/%Y %I:%M %p")
                        
                        # Renew Button
                        btn = InlineKeyboardMarkup([[InlineKeyboardButton("💎 Active Plan Now", callback_data="activate_plan")]])
                        
                        msg_text = None
                        
                        # --- REMINDER LOGIC (Checks every 60s) ---
                        
                        # 12 Hours Left (43200 sec) - Check window: 43200 to 43260
                        if 43200 <= seconds < 43260:
                            msg_text = f"<b>⚠️ Premium Expiring Soon!</b>\n\nYour premium plan expires in <b>12 Hours</b>.\n📅 <b>Expiry:</b> <code>{expiry_str}</code>"
                        
                        # 6 Hours Left
                        elif 21600 <= seconds < 21660:
                            msg_text = f"<b>⚠️ Premium Expiring Soon!</b>\n\nYour premium plan expires in <b>6 Hours</b>.\n📅 <b>Expiry:</b> <code>{expiry_str}</code>"
                            
                        # 3 Hours Left
                        elif 10800 <= seconds < 10860:
                            msg_text = f"<b>⚠️ Premium Expiring Soon!</b>\n\nYour premium plan expires in <b>3 Hours</b>.\n📅 <b>Expiry:</b> <code>{expiry_str}</code>"
                            
                        # 1 Hour Left
                        elif 3600 <= seconds < 3660:
                            msg_text = f"<b>⚠️ Premium Expiring Soon!</b>\n\nYour premium plan expires in <b>1 Hour</b>.\n📅 <b>Expiry:</b> <code>{expiry_str}</code>"
                            
                        # 10 Minutes Left
                        elif 600 <= seconds < 660:
                            msg_text = f"<b>⚠️ Premium Expiring Soon!</b>\n\nYour premium plan expires in <b>10 Minutes</b>.\n📅 <b>Expiry:</b> <code>{expiry_str}</code>"
                            
                        # Expired (<= 0)
                        elif seconds <= 0:
                            msg_text = f"<b>❌ Premium Expired!</b>\n\nYour premium plan has expired on <b>{expiry_str}</b>.\n\nRenew now to continue enjoying exclusive features."
                            # Remove Premium Status from DB immediately
                            await db.update_plan(user_id, {'expire': '', 'trial': False, 'plan': '', 'premium': False})
                        
                        # Send Message if condition met
                        if msg_text:
                            try:
                                await self.send_message(chat_id=user_id, text=msg_text, reply_markup=btn)
                            except Exception as e:
                                logging.error(f"Could not send reminder to {user_id}: {e}")
                                
                    except Exception as e:
                        logging.error(f"Error checking user {user.get('id')}: {e}")
                        
            except Exception as e:
                logging.error(f"Error in premium checker loop: {e}")
            
            # Wait for 60 seconds before next check
            await asyncio.sleep(60)

if __name__ == "__main__":
    # Event Loop Policy for Python 3.11+
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        pass
        
    Bot().run()
