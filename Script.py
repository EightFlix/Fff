class script(object):

    START_TXT = """<b>ʜᴇʏ {}, <i>{}</i></b><br>    <br><b>Premium Filter With PM Search ⚡</b>"""

    MY_ABOUT_TXT = """★ Server: <a href=https://koyeb.com>Koyeb</a><br>★ Database: <a href=https://www.mongodb.com>MongoDB</a><br>★ Language: <a href=https://www.python.org>Python</a><br>★ Library: <a href=https://t.me/HydrogramNews>Hydrogram</a>"""

    MY_OWNER_TXT = """★ Name: Admin<br>★ Contact: <a href=https://t.me/YourX>Support</a>"""

    STATUS_TXT = """👤 Total Users: <code>{}</code><br>😎 Premium Users: <code>{}</code><br>👥 Total Chats: <code>{}</code><br>🗳 Data database used: <code>{}</code><br><br>🗂 Files Indexed: <code>{}</code><br>🗳 Files DB used: <code>{}</code><br><br>🚀 Bot Uptime: <code>{}</code>"""

    NEW_GROUP_TXT = """#NewGroup<br>Title - {}<br>ID - <code>{}</code><br>Username - {}<br>Total - <code>{}</code>"""

    NEW_USER_TXT = """#NewUser<br>★ Name: {}<br>★ ID: <code>{}</code>"""

    NOT_FILE_TXT = """👋 Hello {},<br><br>I can't find the <b>{}</b> in my database! 🥲<br><br>👉 Check your spelling.<br>👉 Or it has not been released yet."""
    
    IMDB_TEMPLATE = """✅ I Found: <code>{query}</code><br><br>🏷 Title: <a href={url}>{title}</a><br>🎭 Genres: {genres}<br>📆 Year: <a href={url}/releaseinfo>{year}</a><br>🌟 Rating: <a href={url}/ratings>{rating} / 10</a><br>☀️ Languages: {languages}<br>📀 RunTime: {runtime} Minutes<br><br>🗣 Requested by: {message.from_user.mention}<br>©️ Powered by: <b>{message.chat.title}</b>"""

    FILE_CAPTION = """<b>📂 {file_name}</b><br><b>♻️ Size: {file_size}</b><br><b>⚡ Powered By:- @YourXCloud</b>"""

    WELCOME_TEXT = """👋 Hello {mention}, Welcome to {title} group! 💞"""

    HELP_TXT = """👋 Hello {},<br>    <br>I can filter movie and series you want<br>Just type you want movie or series in my PM or adding me in to group<br>And i have more feature for you<br>Just try my commands"""

    # Removed /set_req_fsub and /delreq from here
    ADMIN_COMMAND_TXT = """<b>Here is bot admin commands 👇<br><br>
/index_channels - to check how many index channel id added
/stats - to get bot status
/delete - to delete files using query
/delete_all - to delete all indexed file
/broadcast - to send message to all bot users
/on_auto_filter - On Auto Filter
/off_pm_search - Off Pm Search
/on_pm_search  - On Pm Search
/restart - to restart bot
/leave - to leave your bot from particular group
/users - to get all users details
/chats - to get all groups
/invite_link - to generate invite link
/index - to index bot accessible channels
/add_prm - to add new premium user
/rm_prm - to add remove premium user
/set_fsub - to set force subscribe channels</b>"""
    
    PLAN_TXT = """Activate any premium plan to get exclusive features.<br><br>You can activate any premium plan and then you can get exclusive features.<br><br>- INR {} for pre day -<br><br>Basic premium features:<br>Ad free experience<br>Online watch and fast download<br>No need joind channels<br>No need verify<br>No shortlink<br>Admins support<br>And more...<br><br>Support: {}"""

    USER_COMMAND_TXT = """<b>Here is bot user commands 👇<br><br>/start - to check bot alive or not
/myplan - to check my activated premium plan
/plan - to view premium plan details
/img_2_link - upload image to uguu.se and get link
/settings - to change group settings as your wish
/connect - to connect group settings to PM
/id - to check group or channel id</b>"""
    
    # Source link removed
    SOURCE_TXT = """<b>This is a private bot created for our community.</b>"""
