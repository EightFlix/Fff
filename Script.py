class script(object):

    START_TXT = """<b>ʜᴇʏ {}, <i>{}</i></b><br>    <br><b>Premium Filter With PM Search ⚡</b>"""

    # Stats Format
    STATUS_TXT = """<b>🗃 Total Files:</b> <code>{}</code>
<b>👤 Total Users:</b> <code>{}</code>
<b>💬 Total Chats:</b> <code>{}</code>
<b>🚀 Premium Users:</b> <code>{}</code>

<b>📂 Used Storage:</b> <code>{}</code>
<b>🗂 Free Storage:</b> <code>{}</code>
<b>⏰ Uptime:</b> <code>{}</code>"""

    NEW_GROUP_TXT = """#NewGroup<br>Title - {}<br>ID - <code>{}</code><br>Username - {}<br>Total - <code>{}</code>"""
    NEW_USER_TXT = """#NewUser<br>★ Name: {}<br>★ ID: <code>{}</code>"""
    NOT_FILE_TXT = """👋 Hello {},<br><br>I can't find the <b>{}</b> in my database! 🥲"""
    
    # Variables required by info.py (Do not remove these names, just keep values simple)
    IMDB_TEMPLATE = """✅ I Found: <code>{query}</code><br><br>🏷 Title: <a href={url}>{title}</a>"""
    FILE_CAPTION = """<b>📂 {file_name}</b><br><b>♻️ Size: {file_size}</b><br><b>⚡ Powered By:- @YourXCloud</b>"""
    WELCOME_TEXT = """👋 Hello {mention}, Welcome to {title} group! 💞"""

    HELP_TXT = """👋 Hello {},<br>    <br>I can filter movie and series you want.<br>Just type the name in PM or Group.<br><br><b>Click buttons below for command list.</b>"""

    ADMIN_COMMAND_TXT = """<b>👮‍♂️ Admin Commands:</b>

<b>🗂 Indexing:</b>
• /index_channels - List Index Channels
• /add_channel - Add Index Channel
• /remove_channel - Remove Index Channel
• /delete - Delete specific file
• /delete_all - Delete ALL files

<b>📢 Force Subscribe:</b>
• /add_fsub - Add F-Sub Channel
• /del_fsub - Remove F-Sub
• /view_fsub - View Settings

<b>👥 User & Chat Management:</b>
• /users - List all users
• /chats - List all groups
• /ban_user - Ban a user
• /unban_user - Unban a user
• /ban_grp - Disable Group
• /unban_grp - Enable Group
• /leave - Leave a group

<b>💎 Premium:</b>
• /add_prm - Add Premium
• /rm_prm - Remove Premium
• /prm_list - List Premium Users

<b>⚙️ Bot Settings:</b>
• /stats - Check Bot Status
• /broadcast - Broadcast Message
• /restart - Restart the bot
• /on_auto_filter - Enable Auto Filter
• /off_auto_filter - Disable Auto Filter
• /on_pm_search - Enable PM Search
• /off_pm_search - Disable PM Search"""
    
    PLAN_TXT = """<b>💎 Premium Plans</b>\n\nActivate premium to get exclusive features like:\n• Ad-free experience\n• Direct Links\n• Fast Download\n\n<b>💰 Price:</b> INR {} per day\n\n<b>UPI ID:</b> <code>{}</code>"""

    USER_COMMAND_TXT = """<b>👤 User Commands:</b>

• /start - Check bot alive
• /myplan - Check your premium status
• /plan - Activate new plan
• /id - Get Telegram ID
• /img_2_link - Convert Image to Link
• /settings - Change Group Settings (Admins only)"""
