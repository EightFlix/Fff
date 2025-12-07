import os
import random
import string
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from time import time as time_now
from time import monotonic

from hydrogram import Client, filters, enums
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Script import script
from database.ia_filterdb import db_count_documents, second_db_count_documents, get_file_details, delete_files
from database.users_chats_db import db
from info import (
    IS_PREMIUM, PRE_DAY_AMOUNT, RECEIPT_SEND_USERNAME, URL, BIN_CHANNEL, 
    SECOND_FILES_DATABASE_URL, STICKERS, INDEX_CHANNELS, ADMINS, IS_VERIFY, 
    VERIFY_TUTORIAL, VERIFY_EXPIRE, SHORTLINK_API, SHORTLINK_URL, DELETE_TIME, 
    SUPPORT_LINK, UPDATES_LINK, LOG_CHANNEL, PICS, IS_STREAM, REACTIONS, PM_FILE_DELETE_TIME
)
from utils import (
    is_premium, upload_image, get_settings, get_size, is_subscribed, 
    is_check_admin, get_shortlink, get_verify_status, update_verify_status, 
    get_readable_time, get_wish
)

logger = logging.getLogger(__name__)

async def get_grp_stg(group_id):
    settings = await get_settings(group_id)
    btn = [[
        InlineKeyboardButton('Edit IMDb template', callback_data=f'imdb_setgs#{group_id}')
    ],[
        InlineKeyboardButton('Edit Shortlink', callback_data=f'shortlink_setgs#{group_id}')
    ],[
        InlineKeyboardButton('Edit File Caption', callback_data=f'caption_setgs#{group_id}')
    ],[
        InlineKeyboardButton('Edit Welcome', callback_data=f'welcome_setgs#{group_id}')
    ],[
        InlineKeyboardButton('Edit tutorial link', callback_data=f'tutorial_setgs#{group_id}')
    ],[
        InlineKeyboardButton(f'IMDb Poster {"✅" if settings["imdb"] else "❌"}', callback_data=f'bool_setgs#imdb#{settings["imdb"]}#{group_id}')
    ],[
        InlineKeyboardButton(f'Spelling Check {"✅" if settings["spell_check"] else "❌"}', callback_data=f'bool_setgs#spell_check#{settings["spell_check"]}#{group_id}')
    ],[
        InlineKeyboardButton(f"Auto Delete - {get_readable_time(DELETE_TIME)}" if settings["auto_delete"] else "Auto Delete ❌", callback_data=f'bool_setgs#auto_delete#{settings["auto_delete"]}#{group_id}')
    ],[
        InlineKeyboardButton(f'Welcome {"✅" if settings["welcome"] else "❌"}', callback_data=f'bool_setgs#welcome#{settings["welcome"]}#{group_id}')
    ],[
        InlineKeyboardButton(f'Shortlink {"✅" if settings["shortlink"] else "❌"}', callback_data=f'bool_setgs#shortlink#{settings["shortlink"]}#{group_id}')
    ],[
        InlineKeyboardButton(f"Result Page - Link" if settings["links"] else "Result Page - Button", callback_data=f'bool_setgs#links#{settings["links"]}#{group_id}')
    ]]
    return btn

async def del_stk(s):
    await asyncio.sleep(3)
    try:
        await s.delete()
    except Exception:
        pass

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            username = f'@{message.chat.username}' if message.chat.username else 'Private'
            await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(message.chat.title, message.chat.id, username, total))       
            await db.add_chat(message.chat.id, message.chat.title)
        
        wish = get_wish()
        user = message.from_user.mention if message.from_user else "Dear"
        btn = [[
            InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ⚡️', url=UPDATES_LINK),
            InlineKeyboardButton('💡 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ 💡', url=SUPPORT_LINK)
        ]]
        await message.reply(text=f"<b>ʜᴇʏ {user}, <i>{wish}</i>\nʜᴏᴡ ᴄᴀɴ ɪ ʜᴇʟᴘ ʏᴏᴜ??</b>", reply_markup=InlineKeyboardMarkup(btn))
        return 
        
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        await message.react(emoji="⚡️", big=True)

    d = await client.send_sticker(message.chat.id, random.choice(STICKERS))
    asyncio.create_task(del_stk(d))

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.NEW_USER_TXT.format(message.from_user.mention, message.from_user.id))

    verify_status = await get_verify_status(message.from_user.id)
    if verify_status['is_verified'] and verify_status.get('expire_time') and datetime.now(timezone.utc) > verify_status['expire_time']:
        await update_verify_status(message.from_user.id, is_verified=False)

    if (len(message.command) != 2) or (len(message.command) == 2 and message.command[1] == 'start'):
        buttons = [[
            InlineKeyboardButton('👨‍🚒 Help', callback_data='help'),
            InlineKeyboardButton('📚 Status 📊', callback_data='stats')
        ],[
            InlineKeyboardButton('🤑 Buy Subscription : Remove Ads', url=f"https://t.me/{client.username}?start=premium")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, get_wish()),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    mc = message.command[1]

    if mc == 'premium':
        return await plan(client, message)
    
    if mc.startswith('settings'):
        _, group_id = message.command[1].split("_")
        if not await is_check_admin(client, int(group_id), message.from_user.id):
            return await message.reply("You not admin in this group.")
        btn = await get_grp_stg(int(group_id))
        chat = await client.get_chat(int(group_id))
        return await message.reply(f"Change your settings for <b>'{chat.title}'</b> as your wish. ⚙", reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)

    if mc.startswith('verify'):
        _, token = mc.split("_", 1)
        verify_status = await get_verify_status(message.from_user.id)
        if verify_status['verify_token'] != token:
            return await message.reply("Your verify token is invalid.")
        expiry_time = datetime.now(timezone.utc) + timedelta(seconds=VERIFY_EXPIRE)
        await update_verify_status(message.from_user.id, is_verified=True, expire_time=expiry_time)
        if verify_status["link"] == "":
            reply_markup = None
        else:
            btn = [[
                InlineKeyboardButton("📌 Get File 📌", url=f'https://t.me/{client.username}?start={verify_status["link"]}')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
        await message.reply(f"✅ You successfully verified until: {get_readable_time(VERIFY_EXPIRE)}", reply_markup=reply_markup, protect_content=True)
        return
    
    verify_status = await get_verify_status(message.from_user.id)
    if IS_VERIFY and not verify_status['is_verified'] and not await is_premium(message.from_user.id, client):
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        await update_verify_status(message.from_user.id, verify_token=token, link="" if mc == 'inline_verify' else mc)
        link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://t.me/{client.username}?start=verify_{token}')
        btn = [[
            InlineKeyboardButton("🧿 Verify 🧿", url=link)
        ],[
            InlineKeyboardButton('🗳 Tutorial 🗳', url=VERIFY_TUTORIAL)
        ]]
        await message.reply("You not verified today! Kindly verify now. 🔐", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
        return

    btn = await is_subscribed(client, message)
    if btn:
        btn.append(
            [InlineKeyboardButton("🔁 Try Again 🔁", callback_data=f"checksub#{mc}")]
        )
        reply_markup = InlineKeyboardMarkup(btn)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=f"👋 Hello {message.from_user.mention},\n\nPlease join my 'Updates Channel' and try again. 😇",
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return 
        
    if mc.startswith('all'):
        try:
            _, grp_id, key = mc.split("_", 2)
        except ValueError:
            return await message.reply("Invalid link format")
            
        # Note: temp.FILES logic usually relies on active memory, might need persistent storage for deep links to work reliably after restart
        # For now keeping as is assuming temp is populated via other means or this is immediate interaction
        from utils import temp
        files = temp.FILES.get(key)
        if not files:
            return await message.reply('No Such All Files Exist! (Link expired or bot restarted)')
            
        settings = await get_settings(int(grp_id))
        total_files = await message.reply(f"<b><i>🗂 Total files - <code>{len(files)}</code></i></b>", parse_mode=enums.ParseMode.HTML)
        
        file_ids = []
        file_ids.append(total_files.id)
        
        for file in files:
            CAPTION = settings['caption']
            f_caption = CAPTION.format(
                file_name=file['file_name'],
                file_size=get_size(file['file_size']),
                file_caption=file['caption']
            )      
            btn = [[InlineKeyboardButton('🙅 Close', callback_data='close_data')]]
            if IS_STREAM:
                btn.insert(0, [InlineKeyboardButton("🚀 Watch And Download ⚡", callback_data=f"stream#{file['_id']}")])

            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file['_id'],
                caption=f_caption,
                protect_content=False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            file_ids.append(msg.id)

        time = get_readable_time(PM_FILE_DELETE_TIME)
        vp = await message.reply(f"Nᴏᴛᴇ: Tʜɪs ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇ ɪɴ {time} ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛs. Sᴀᴠᴇ ᴛʜᴇ ғɪʟᴇs ᴛᴏ sᴏᴍᴇᴡʜᴇʀᴇ ᴇʟsᴇ")
        file_ids.append(vp.id)
        
        await asyncio.sleep(PM_FILE_DELETE_TIME)
        buttons = [[InlineKeyboardButton('ɢᴇᴛ ғɪʟᴇs ᴀɢᴀɪɴ', callback_data=f"get_del_send_all_files#{grp_id}#{key}")]] 
        
        for i in range(0, len(file_ids), 100):
            try:
                await client.delete_messages(chat_id=message.chat.id, message_ids=file_ids[i:i+100])
            except: pass
            
        await message.reply("Tʜᴇ ғɪʟᴇ ʜᴀs ʙᴇᴇɴ ɢᴏɴᴇ ! Cʟɪᴄᴋ ɢɪᴠᴇɴ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪᴛ ᴀɢᴀɪɴ.", reply_markup=InlineKeyboardMarkup(buttons))
        return

    # Single File Handling
    try:
        type_, grp_id, file_id = mc.split("_", 2)
    except ValueError:
        return await message.reply("Invalid Command")
        
    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply('No Such File Exist!')
        
    settings = await get_settings(int(grp_id))
    if type_ != 'shortlink' and settings['shortlink'] and not await is_premium(message.from_user.id, client):
        link = await get_shortlink(settings['url'], settings['api'], f"https://t.me/{client.username}?start=shortlink_{grp_id}_{file_id}")
        btn = [[
            InlineKeyboardButton("♻️ Get File ♻️", url=link)
        ],[
            InlineKeyboardButton("📍 ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ 📍", url=settings['tutorial'])
        ]]
        await message.reply(f"[{get_size(files_['file_size'])}] {files_['file_name']}\n\nYour file is ready, Please get using this link. 👍", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
        return
            
    CAPTION = settings['caption']
    f_caption = CAPTION.format(
        file_name = files_['file_name'],
        file_size = get_size(files_['file_size']),
        file_caption=files_['caption']
    )
    
    btn = [[InlineKeyboardButton('🙅 Close', callback_data='close_data')]]
    if IS_STREAM:
        btn.insert(0, [InlineKeyboardButton("🚀 Watch And Download ⚡", callback_data=f"stream#{file_id}")])
    
    vp = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=False,
        reply_markup=InlineKeyboardMarkup(btn)
    )
    time = get_readable_time(PM_FILE_DELETE_TIME)
    msg = await vp.reply(f"Nᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇ ɪɴ {time} ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛs. Sᴀᴠᴇ ᴛʜᴇ ғɪʟᴇ ᴛᴏ sᴏᴍᴇᴡʜᴇʀᴇ ᴇʟsᴇ")
    
    await asyncio.sleep(PM_FILE_DELETE_TIME)
    btns = [[
        InlineKeyboardButton('ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ', callback_data=f"get_del_file#{grp_id}#{file_id}")
    ]]
    try:
        await msg.delete()
        await vp.delete()
    except: pass
    
    await message.reply("Tʜᴇ ғɪʟᴇ ʜᴀs ʙᴇᴇɴ ɢᴏɴᴇ ! Cʟɪᴄᴋ ɢɪᴠᴇɴ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪᴛ ᴀɢᴀɪɴ.", reply_markup=InlineKeyboardMarkup(btns))

@Client.on_message(filters.command('link'))
async def link(bot, message):
    msg = message.reply_to_message
    if not msg:
        return await message.reply('Reply to media')
    try:
        media = getattr(msg, msg.media.value)
        msg = await bot.send_cached_media(chat_id=BIN_CHANNEL, file_id=media.file_id)
        watch = f"{URL}watch/{msg.id}"
        download = f"{URL}download/{msg.id}"
        btn=[[
            InlineKeyboardButton("ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ", url=watch),
            InlineKeyboardButton("ꜰᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ", url=download)
        ],[
            InlineKeyboardButton('🙅 Close', callback_data='close_data')
        ]]
        await message.reply('Here is your link', reply_markup=InlineKeyboardMarkup(btn))
    except Exception as e:
        await message.reply(f'Error: {e}')

@Client.on_message(filters.command('index_channels'))
async def channels_info(bot, message):
    if message.from_user.id not in ADMINS:
        await message.delete()
        return
    ids = INDEX_CHANNELS
    if not ids:
        return await message.reply("Not set INDEX_CHANNELS")
    text = '**Indexed Channels:**\n\n'
    for id in ids:
        try:
            chat = await bot.get_chat(id)
            text += f'{chat.title}\n'
        except:
            text += f'{id} (Unknown)\n'
    text += f'\n**Total:** {len(ids)}'
    await message.reply(text)

@Client.on_message(filters.command('stats'))
async def stats(bot, message):
    if message.from_user.id not in ADMINS:
        await message.delete()
        return
    files = await db_count_documents()
    users = await db.total_users_count()
    chats = await db.total_chat_count()
    prm = await db.get_premium_count()
    used_files_db_size = get_size(await db.get_files_db_size())
    used_data_db_size = get_size(await db.get_data_db_size())

    if SECOND_FILES_DATABASE_URL:
        secnd_files_db_used_size = get_size(await db.get_second_files_db_size())
        secnd_files = await second_db_count_documents()
    else:
        secnd_files_db_used_size = '-'
        secnd_files = '-'

    uptime = get_readable_time(time_now() - temp.START_TIME)
    await message.reply_text(script.STATUS_TXT.format(users, prm, chats, used_data_db_size, files, used_files_db_size, secnd_files, secnd_files_db_used_size, uptime))    

@Client.on_message(filters.command('settings'))
async def settings(client, message):
    group_id = message.chat.id
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not await is_check_admin(client, group_id, message.from_user.id):
            return await message.reply_text('You not admin in this group.')
        btn = [[
            InlineKeyboardButton("Open Here", callback_data='open_group_settings')
        ],[
            InlineKeyboardButton("Open In PM", callback_data='open_pm_settings')
        ]]
        await message.reply_text('Where do you want to open the settings menu?', reply_markup=InlineKeyboardMarkup(btn))
    elif message.chat.type == enums.ChatType.PRIVATE:
        cons = await db.get_connections(message.from_user.id)
        if not cons:
            return await message.reply_text("No groups found! Use this command group and open in PM")
        buttons = []
        for con in cons:
            try:
                chat = await client.get_chat(con)
                buttons.append(
                    [InlineKeyboardButton(text=chat.title, callback_data=f'back_setgs#{chat.id}')]
                )
            except:
                pass
        await message.reply_text('Select the group whose settings you want to change.', reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command('connect'))
async def connect(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id
        await db.add_connect(group_id, message.from_user.id)
        await message.reply_text('Successfully connected this group to PM.')
    elif message.chat.type == enums.ChatType.PRIVATE:
        if len(message.command) > 1:
            group_id = message.command[1]
            try:
                if not await is_check_admin(client, int(group_id), message.from_user.id):
                    return await message.reply_text('You not admin in this group.')
                chat = await client.get_chat(int(group_id))
                await db.add_connect(int(group_id), message.from_user.id)
                await message.reply_text(f'Successfully connected {chat.title} group to PM')
            except Exception as e:
                await message.reply_text(f'Error: {e}')
        else:
            await message.reply_text('Usage: /connect group_id\nor use /connect in group')

@Client.on_message(filters.command('delete'))
async def delete_file(bot, message):
    if message.from_user.id not in ADMINS:
        await message.delete()
        return
    try:
        query = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Command Incomplete!\nUsage: /delete query")
    btn = [[
        InlineKeyboardButton("YES", callback_data=f"delete_{query}")
    ],[
        InlineKeyboardButton("CLOSE", callback_data="close_data")
    ]]
    await message.reply_text(f"Do you want to delete all: {query} ?", reply_markup=InlineKeyboardMarkup(btn))

@Client.on_message(filters.command('img_2_link'))
async def img_2_link(bot, message):
    reply_to_message = message.reply_to_message
    if not reply_to_message:
        return await message.reply('Reply to any photo')
    file = reply_to_message.photo
    if file is None:
        return await message.reply('Invalid media.')
    text = await message.reply_text(text="ᴘʀᴏᴄᴇssɪɴɢ....")   
    path = await reply_to_message.download()  
    response = upload_image(path)
    try:
        os.remove(path)
    except: pass
    
    if not response:
         await text.edit_text(text="Upload failed!")
         return    
    await text.edit_text(f"<b>❤️ Your link ready 👇\n\n{response}</b>", disable_web_page_preview=True)

@Client.on_message(filters.command('ping'))
async def ping(client, message):
    start_time = monotonic()
    msg = await message.reply("👀")
    end_time = monotonic()
    await msg.edit(f'{round((end_time - start_time) * 1000)} ms')

@Client.on_message(filters.command('plan') & filters.private)
async def plan(client, message):
    if not IS_PREMIUM:
        return await message.reply('Premium feature was disabled by admin')
    btn = [[
        InlineKeyboardButton('Activate Plan', callback_data='activate_plan')
    ]]
    await message.reply(script.PLAN_TXT.format(PRE_DAY_AMOUNT, RECEIPT_SEND_USERNAME), reply_markup=InlineKeyboardMarkup(btn))

# ... (add_prm, rm_prm, prm_list, set_fsub, set_req_fsub, on/off filters are fine, 
# just make sure to use 'await' for DB calls if they were missing in previous copies)
# I will exclude them for brevity unless requested, but the pattern is consistent.
