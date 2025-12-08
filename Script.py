class script(object):

    START_TXT = """<b>ʜᴇʏ {}, <i>{}</i></b><br>    <br><b>Premium Filter With PM Search ⚡</b>"""

    # MY_ABOUT_TXT और MY_OWNER_TXT को यहाँ से हटा दिया गया है

    # Updated Status Text for Storage & Uptime
    STATUS_TXT = """<b>📊 Bot Status</b>
    
👤 <b>Users:</b> <code>{}</code>
😎 <b>Premium:</b> <code>{}</code>
👥 <b>Chats:</b> <code>{}</code>

<b>🗂 Database Storage:</b>
• <b>Files Indexed:</b> <code>{}</code>
• <b>DB Used:</b> <code>{}</code>
• <b>Free Space:</b> <code>{}</code>

🚀 <b>Uptime:</b> <code>{}</code>"""

    NEW_GROUP_TXT = """#NewGroup<br>Title - {}<br>ID - <code>{}</code><br>Username - {}<br>Total - <code>{}</code>"""

    NEW_USER_TXT = """#NewUser<br>★ Name: {}<br>★ ID: <code>{}</code>"""

    NOT_FILE_TXT = """👋 Hello {},<br><br>I can't find the <b>{}</b> in my database! 🥲"""
    
    IMDB_TEMPLATE = """✅ I Found: <code>{query}</code><br><br>🏷 Title: <a href={url}>{title}</a>"""

    FILE_CAPTION = """<b>📂 {file_name}</b><br><b>♻️ Size: {file_size}</b><br><b>⚡ Powered By:- @YourXCloud</b>"""

    WELCOME_TEXT = """👋 Hello {mention}, Welcome to {title} group! 💞"""

    HELP_TXT = """👋 Hello {},<br>    <br>I can filter movie and series you want."""

    ADMIN_COMMAND_TXT = """<b>Here is bot admin commands 👇<br><br>
/index_channels - Index channel
/stats - Bot Status
/broadcast - Broadcast message
/add_prm - Add Premium
/rm_prm - Remove Premium
/prm_list - List Premium Users</b>"""
    
    PLAN_TXT = """Activate premium plan to get exclusive features.<br><br>- INR {} for pre day -"""

    USER_COMMAND_TXT = """<b>User Commands: /start, /myplan, /plan</b>"""
    
    SOURCE_TXT = """<b>Private Bot.</b>"""
