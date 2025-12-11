class script(object):

    # --- 👋 START MESSAGE ---
    # Used in: commands.py (start)
    START_TXT = """<b>👋 Hᴇʟʟᴏ {}, {}!</b>

I ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ <b>Pʀᴇᴍɪᴜᴍ Aᴜᴛᴏ Fɪʟᴛᴇʀ Bᴏᴛ</b>. ⚡
I ᴄᴀɴ ᴘʀᴏᴠɪᴅᴇ ᴍᴏᴠɪᴇs, sᴇʀɪᴇs, ᴀɴᴅ ғɪʟᴇs ᴅɪʀᴇᴄᴛʟʏ ɪɴ ʏᴏᴜʀ PM ᴏʀ Gʀᴏᴜᴘ.

✨ <b><u>Mʏ Fᴇᴀᴛᴜʀᴇs:</u></b>
🚀 <b>Fᴀsᴛ Sᴇᴀʀᴄʜ:</b> Get files in milliseconds.
🛡️ <b>Sᴇᴄᴜʀᴇ:</b> No Ads & Direct Links (Premium).
🎥 <b>Sᴛʀᴇᴀᴍɪɴɢ:</b> Watch Online without downloading.
📂 <b>Sᴍᴀʀᴛ Iɴᴅᴇx:</b> Auto-index channels support.

<i>👇 Cʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ!</i>"""

    # --- 📊 STATUS DASHBOARD ---
    # Used in: commands.py (stats)
    STATUS_TXT = """<b>📊 <u>Sʏsᴛᴇᴍ Sᴛᴀᴛɪsᴛɪᴄs</u></b>

<b>📂 Tᴏᴛᴀʟ Fɪʟᴇs:</b> <code>{}</code>
<b>👤 Tᴏᴛᴀʟ Usᴇʀs:</b> <code>{}</code>
<b>🏘️ Tᴏᴛᴀʟ Gʀᴏᴜᴘs:</b> <code>{}</code>
<b>💎 Pʀᴇᴍɪᴜᴍ Usᴇʀs:</b> <code>{}</code>

<b>💾 Sᴛᴏʀᴀɢᴇ:</b> <code>{} / {}</code>
<b>⚡ Uᴘᴛɪᴍᴇ:</b> <code>{}</code>"""

    # --- ⚙️ HELP MENU ---
    # Used in: pm_filter.py (help callback)
    HELP_TXT = """<b>⚙️ <u>Hᴇʟᴘ Mᴇɴᴜ</u></b>

Hᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ғɪɴᴅ ᴀʟʟ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs ᴀɴᴅ ɪɴsᴛʀᴜᴄᴛɪᴏɴs ᴛᴏ ᴜsᴇ ᴍᴇ.

👤 <b>Usᴇʀs:</b> Learn how to search & download.
🦹 <b>Aᴅᴍɪɴs:</b> Learn how to manage groups & files.

<i>👇 Cʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ:</i>"""

    # --- 👤 USER COMMANDS ---
    USER_COMMAND_TXT = """<b>👤 <u>Usᴇʀ Cᴏᴍᴍᴀɴᴅs</u></b>

🔹 <code>/start</code> - Check if I am alive.
🔹 <code>/link</code> - Get Stream/Download Link (Reply to file).
🔹 <code>/plan</code> - Check Premium Plans.
🔹 <code>/myplan</code> - Check your current status.
🔹 <code>/id</code> - Get your Telegram ID.
🔹 <code>/info</code> - Get User Information.
🔹 <code>/img_2_link</code> - Create Link from Image.

<b>🔍 Hᴏᴡ ᴛᴏ Sᴇᴀʀᴄʜ?</b>
Just type the <b>Movie or Series Name</b> in the Group or PM, and I will send the files."""

    # --- 🦹 ADMIN COMMANDS ---
    ADMIN_COMMAND_TXT = """<b>🦹 <u>Aᴅᴍɪɴ Cᴏᴍᴍᴀɴᴅs</u></b>

<b>🗂️ Iɴᴅᴇxɪɴɢ Oᴘᴇʀᴀᴛɪᴏɴs:</b>
🔹 <code>/index_channels</code> - List indexed channels.
🔹 <code>/add_channel [ID]</code> - Add a channel for indexing.
🔹 <code>/remove_channel [ID]</code> - Remove a channel.
🔹 <code>/delete [Query]</code> - Delete specific files from DB.
🔹 <code>/delete_all</code> - Delete ALL files (Reset DB).

<b>📢 Bʀᴏᴀᴅᴄᴀsᴛ & F-Sᴜʙ:</b>
🔹 <code>/broadcast</code> - Send message to all users/groups.
🔹 <code>/add_fsub [ID]</code> - Set Force Subscribe Channel.
🔹 <code>/del_fsub</code> - Remove Force Subscribe.
🔹 <code>/view_fsub</code> - Check F-Sub Settings.

<b>👥 Mᴏᴅᴇʀᴀᴛɪᴏɴ:</b>
🔹 <code>/users</code> - List all users in DB.
🔹 <code>/chats</code> - List all groups in DB.
🔹 <code>/ban_user [ID]</code> - Ban a user from bot.
🔹 <code>/unban_user [ID]</code> - Unban a user.
🔹 <code>/ban_grp [ID]</code> - Disable bot in a group.
🔹 <code>/leave [ID]</code> - Force leave a group.

<b>💎 Pʀᴇᴍɪᴜᴍ Mᴀɴᴀɢᴇᴍᴇɴᴛ:</b>
🔹 <code>/add_prm [ID] [Days]</code> - Give Premium manually.
🔹 <code>/rm_prm [ID]</code> - Remove Premium.
🔹 <code>/prm_list</code> - List all Premium users.

<b>⚙️ Sʏsᴛᴇᴍ:</b>
🔹 <code>/stats</code> - Check Bot Statistics.
🔹 <code>/restart</code> - Restart the bot server.
🔹 <code>/eval</code> - Execute Python Code."""

    # --- 💎 PREMIUM PLAN ---
    # Used in: commands.py (plan)
    PLAN_TXT = """<b>💎 <u>Pʀᴇᴍɪᴜᴍ Uᴘɢʀᴀᴅᴇ</u></b>

<i>Uɴʟᴏᴄᴋ ᴛʜᴇ ғᴜʟʟ ᴘᴏᴛᴇɴᴛɪᴀʟ ᴏғ Fᴀsᴛ Fɪɴᴅᴇʀ!</i> 🚀

✅ <b>Nᴏ Aᴅs & Cᴀᴘᴛᴄʜᴀ</b>
✅ <b>Dɪʀᴇᴄᴛ Dᴏᴡɴʟᴏᴀᴅ Lɪɴᴋs</b>
✅ <b>Hɪɢʜ Sᴘᴇᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ</b>
✅ <b>Pʀɪᴏʀɪᴛʏ Sᴜᴘᴘᴏʀᴛ</b>

💰 <b>Pʀɪᴄᴇ:</b> ₹{} / Dᴀʏ
<i>(Contact Admin for Custom Plans)</i>

<b>🛍️ Hᴏᴡ ᴛᴏ Bᴜʏ?</b>
1️⃣ Click the button below.
2️⃣ Enter the number of days.
3️⃣ Pay via UPI QR Code.
4️⃣ Send the screenshot to <b>{}</b>."""

    # --- 📝 LOG MESSAGES ---
    NEW_USER_TXT = """<b>#New_User_Started 👤</b>

<b>🙋🏻‍♀️ Nᴀᴍᴇ:</b> {}
<b>🆔 ID:</b> <code>{}</code>
<b>📅 Dᴀᴛᴇ:</b> <i>Today</i>"""

    NEW_GROUP_TXT = """<b>#New_Group_Added 🏘️</b>

<b>🏷️ Tɪᴛʟᴇ:</b> {}
<b>🆔 ID:</b> <code>{}</code>
<b>🔗 Usᴇʀɴᴀᴍᴇ:</b> {}
<b>👥 Tᴏᴛᴀʟ Mᴇᴍʙᴇʀs:</b> <code>{}</code>"""

    # --- ⚠️ LEGACY VARIABLES (Required to prevent errors) ---
    NOT_FILE_TXT = """👋 Hᴇʟʟᴏ {},<br><br>I ᴄᴀɴ'ᴛ ғɪɴᴅ <b>{}</b> ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ! 🥲"""
    IMDB_TEMPLATE = """✅ I Fᴏᴜɴᴅ: <code>{query}</code>""" # Minimal fallback
    FILE_CAPTION = """<b>📂 {file_name}</b>\n<b>💾 Sɪᴢᴇ: {file_size}</b>"""
    WELCOME_TEXT = """<b>👋 Hᴇʟʟᴏ {mention}, Wᴇʟᴄᴏᴍᴇ ᴛᴏ {title}!</b>"""
