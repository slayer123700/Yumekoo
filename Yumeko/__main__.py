import os
import importlib
import asyncio
import json
from pyrogram import idle, filters , Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery , Message
from Yumeko import app, log, telebot, BACKUP_FILE_JSON, ptb, scheduler
from config import config
from Yumeko.helper.on_start import edit_restart_message, clear_downloads_folder, notify_startup
from Yumeko.admin.roleassign import ensure_owner_is_hokage
from Yumeko.helper.state import initialize_services
from Yumeko.database import setup_indexes, db
from Yumeko.admin.backup import restore_db
from asyncio import sleep
from Yumeko.decorator.save import save 
from Yumeko.decorator.errors import error 

MODULES = ["modules", "watchers", "admin", "decorator"]
LOADED_MODULES = {}

# Load modules and extract __module__ and __help__
def load_modules_from_folder(folder_name):
    folder_path = os.path.join(os.path.dirname(__file__), folder_name)
    for filename in os.listdir(folder_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"Yumeko.{folder_name}.{module_name}")
            __module__ = getattr(module, "__module__", None)
            __help__ = getattr(module, "__help__", None)
            if __module__ and __help__:
                LOADED_MODULES[__module__] = __help__

def load_all_modules():
    for folder in MODULES:
        load_modules_from_folder(folder)
    log.info(f"Loaded {len(LOADED_MODULES)} modules: {', '.join(sorted(LOADED_MODULES.keys()))}")

# Pagination Logic
def get_paginated_buttons(page=1, items_per_page=15):
    modules = sorted(LOADED_MODULES.keys())
    total_pages = (len(modules) + items_per_page - 1) // items_per_page

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_modules = modules[start_idx:end_idx]

    buttons = [
        InlineKeyboardButton(mod, callback_data=f"help_{i}_{page}")
        for i, mod in enumerate(current_modules, start=start_idx)
    ]
    button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    # Navigation buttons logic
    if page == 1:  # First page: Next and Close vertically
        button_rows.append([
            InlineKeyboardButton("➡️", callback_data=f"area_{page + 1}")
        ])
        button_rows.append([
            InlineKeyboardButton("🗑️", callback_data="delete")
        ])
    elif page == total_pages:  # Last page: Back and Close vertically
        button_rows.append([
            InlineKeyboardButton("⬅️", callback_data=f"area_{page - 1}")
        ])
        button_rows.append([
            InlineKeyboardButton("🗑️", callback_data="delete")
        ])
    else:  # Other pages: Back, Close, Next horizontally
        button_rows.append([
            InlineKeyboardButton("⬅️", callback_data=f"area_{page - 1}"),
            InlineKeyboardButton("🗑️", callback_data="delete"),
            InlineKeyboardButton("➡️", callback_data=f"area_{page + 1}")
        ])

    return InlineKeyboardMarkup(button_rows)

# Helper to generate the main menu buttons
def get_main_menu_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                "➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{app.me.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("🤝 Sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT_LINK),
            InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", user_id=config.OWNER_ID)
        ],
        [
            InlineKeyboardButton(" Cᴏᴍᴍᴀɴᴅs 👀 ", callback_data="yumeko_help")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

@app.on_message(filters.command("start" , config.COMMAND_PREFIXES) & filters.private)
@error
@save
async def start_cmd(_, message : Message):
    
    # Check for parameters passed with the start command
    if len(message.command) > 1 and message.command[1] == "help":
        await help_command(Client, message)
        return
    
    x = await message.reply_text(f"`Hie {message.from_user.first_name} <3`")
    await sleep(0.3)
    await x.edit_text("🎊")
    await sleep(0.8)
    await x.edit_text("🎉")
    await sleep(0.8)
    await x.edit_text("⚡️")
    await sleep(0.8)
    await x.delete()
    
    await message.reply_cached_media(file_id = "CAACAgUAAyEFAASjn0HcAAIKDGiIRiZ2LXT6sjoBxPvyFYdPFTJgAAKpFgACfE9IVJy0EWc7L1VlHgQ") 
    
    await sleep(0.2)
    
async def start_handler(client, message):
    user_mention = message.from_user.mention(style="md")
    bot_mention = client.me.mention(style="md")

    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=(
          await message.reply_photo(
    photo=config.START_IMG_URL,
    caption=(
        await message.reply_photo(
    photo=config.START_IMG_URL,
    caption=(
        f"ʜᴇʏ, {user_mention} 🎀\n"
        f"ɪ'ᴍ {bot_mention} ♡💫, ʏᴏᴜʀ ᴍᴜʟᴛɪᴛᴀsᴋɪɴɢ ᴀssɪsᴛᴀɴᴛ ʙᴏᴛ, ʙᴜɪʟᴛ ᴛᴏ sᴛʀᴇᴀᴍʟɪɴᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴡɪᴛʜ ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴏᴏʟs ᴀɴᴅ ғᴇᴀᴛᴜʀᴇs! 🌸\n\n"
        f"✨ ʜᴇʀᴇ's ᴡʜᴀᴛ ɪ ᴄᴀɴ ᴅᴏ:\n\n"
        f"• ᴇғғɪᴄɪᴇɴᴛ ɢʀᴏᴜᴘ sᴜᴘᴇʀᴠɪsɪᴏɴ🛠\n"
        f"• ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴏᴅᴇʀᴀᴛɪᴏɴ ᴏᴘᴛɪᴏɴs🚫\n"
        f"• ᴇɴᴛᴇʀᴛᴀɪɴɪɴɢ ᴀɴᴅ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴍᴏᴅᴜʟᴇs🎮\n\n"
        f"📚 Nᴇᴇᴅ ʜᴇʟᴘ ᴏʀ ᴡᴀɴɴᴀ ᴇxᴘʟᴏʀᴇ?\n"
        f"ᴄʟɪᴄᴋ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ꜰᴏʀ ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs ᴀɴᴅ ᴍᴏᴅᴜʟᴇs. 💬"
    ),
    reply_markup=get_main_menu_buttons()
)

        parse_mode="html"
    )

@app.on_message(filters.command("help", prefixes=config.COMMAND_PREFIXES) & filters.private)
@error
@save
async def help_command(client, message: Message):
    prefixes = " ".join(config.COMMAND_PREFIXES)
    await message.reply(
        text=f"📚 ʜᴇʀᴇ’s ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴀʟʟ ᴍʏ ғᴜɴᴄᴛɪᴏɴᴀʟ ᴍᴏᴅᴜʟᴇs!\n"
             f"🧩 ᴛᴀᴘ ᴏɴ ᴀɴʏ ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ғᴜʟʟ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴀɴᴅ ᴜsᴀɢᴇ. \n\n"
             f"🔧 sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʀᴇғɪxᴇs: {prefixes}\n\n"
             f"[📩]({config.HELP_IMG_URL})🐞 ғᴏᴜɴᴅ ᴀ ʙᴜɢ?\n"
             f"📬 ᴜsᴇ ᴛʜᴇ /bug ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴀɴᴅ ɪ’ʟʟ ғɪx ɪᴛ ᴀs sᴏᴏɴ ᴀs ᴘᴏssɪʙʟᴇ!",
        reply_markup=get_paginated_buttons()
    )

@app.on_callback_query(filters.regex(r"^yumeko_help$"))
async def show_help_menu(client, query: CallbackQuery):
    prefixes = " ".join(config.COMMAND_PREFIXES)
    await query.message.edit(
        𝗍𝖾𝗑𝗍==f"📚 ʜᴇʀᴇ’s ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴀʟʟ ᴍʏ ғᴜɴᴄᴛɪᴏɴᴀʟ ᴍᴏᴅᴜʟᴇs!\n"
             f"🧩 ᴛᴀᴘ ᴏɴ ᴀɴʏ ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ғᴜʟʟ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴀɴᴅ ᴜsᴀɢᴇ. \n\n"
             f"🔧 sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʀᴇғɪxᴇs: {prefixes}\n\n"
             f"[📩]({config.HELP_IMG_URL})🐞 ғᴏᴜɴᴅ ᴀ ʙᴜɢ?\n"
             f"📬 ᴜsᴇ ᴛʜᴇ /bug ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴀɴᴅ ɪ’ʟʟ ғɪx ɪᴛ ᴀs sᴏᴏɴ ᴀs ᴘᴏssɪʙʟᴇ!",
        reply_markup=get_paginated_buttons(),
        invert_media=True
    )

# Callback query handler for module help
@app.on_callback_query(filters.regex(r"^help_\d+_\d+$"))
async def handle_help_callback(client, query: CallbackQuery):
    data = query.data
    try:
        # Extract the numeric index and page from the callback data
        parts = data.split("_")
        module_index = int(parts[1])
        current_page = int(parts[2])

        modules = sorted(LOADED_MODULES.keys())

        # Retrieve the module name using the index
        module_name = modules[module_index]
        help_text = LOADED_MODULES.get(module_name, "No help available for this module.")

        # Edit the message to display the help text
        await query.message.edit(
            text=f"{help_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", callback_data=f"area_{current_page}")]
            ])
        )
    except (ValueError, IndexError) as e:
        await query.answer("Invalid module selected. Please try again.")

# Callback query handler for pagination
@app.on_callback_query(filters.regex(r"^area_\d+$"))
async def handle_pagination_callback(client, query: CallbackQuery):
    data = query.data
    try:
        page = int(data[5:])
        prefixes = " ".join(config.COMMAND_PREFIXES)

        # Edit both the message text and reply markup
        await query.message.edit(
        𝗍𝖾𝗑𝗍==f"📚 ʜᴇʀᴇ’s ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴀʟʟ ᴍʏ ғᴜɴᴄᴛɪᴏɴᴀʟ ᴍᴏᴅᴜʟᴇs!\n"
             f"🧩 ᴛᴀᴘ ᴏɴ ᴀɴʏ ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ғᴜʟʟ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴀɴᴅ ᴜsᴀɢᴇ. \n\n"
             f"🔧 sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʀᴇғɪxᴇs: {prefixes}\n\n"
             f"[📩]({config.HELP_IMG_URL})🐞 ғᴏᴜɴᴅ ᴀ ʙᴜɢ?\n"
             f"📬 ᴜsᴇ ᴛʜᴇ /bug ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴀɴᴅ ɪ’ʟʟ ғɪx ɪᴛ ᴀs sᴏᴏɴ ᴀs ᴘᴏssɪʙʟᴇ!",
            reply_markup=get_paginated_buttons(page),
            invert_media=True
        )
    except Exception as e:
        await query.answer("Error occurred while navigating pages. Please try again.")

# Callback query handler for main menu
@app.on_callback_query(filters.regex(r"^main_menu$"))
async def handle_main_menu_callback(client, query: CallbackQuery):
    prefixes = " ".join(config.COMMAND_PREFIXES)

    await query.message.edit(
        𝗍𝖾𝗑𝗍==f"📚 ʜᴇʀᴇ’s ᴀ ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪsᴛ ᴏғ ᴀʟʟ ᴍʏ ғᴜɴᴄᴛɪᴏɴᴀʟ ᴍᴏᴅᴜʟᴇs!\n"
             f"🧩 ᴛᴀᴘ ᴏɴ ᴀɴʏ ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ғᴜʟʟ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴀɴᴅ ᴜsᴀɢᴇ. \n\n"
             f"🔧 sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʀᴇғɪxᴇs: {prefixes}\n\n"
             f"[📩]({config.HELP_IMG_URL})🐞 ғᴏᴜɴᴅ ᴀ ʙᴜɢ?\n"
             f"📬 ᴜsᴇ ᴛʜᴇ /bug ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴀɴᴅ ɪ’ʟʟ ғɪx ɪᴛ ᴀs sᴏᴏɴ ᴀs ᴘᴏssɪʙʟᴇ!",
        reply_markup=get_paginated_buttons(),
        invert_media=True
    )
    
@app.on_message(filters.command(["start" , "help"], prefixes=config.COMMAND_PREFIXES) & filters.group)
async def start_command(client, message: Message):
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("Sᴛᴀʀᴛ ɪɴ ᴘᴍ", url="https://t.me/shigaraki_probot?start=help")]
    ])
    await message.reply(
        text=f"**𝖧𝖾𝗅𝗅𝗈, {message.from_user.first_name} <3**\n"
             f"𝖢𝗅𝗂𝖼𝗄 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝖾𝗑𝗉𝗅𝗈𝗋𝖾 𝗆𝗒 𝖿𝖾𝖺𝗍𝗎𝗋𝖾𝗌 𝖺𝗇𝖽 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌!",
        reply_markup=button
    )


async def is_database_empty():
    collections = [db.users, db.afk_collection, db.rules_collection, db.announcement_collection]
    for collection in collections:
        if await collection.count_documents({}) > 0:
            return False
    return True

def get_last_backup_file_id():
    if os.path.exists(BACKUP_FILE_JSON):
        with open(BACKUP_FILE_JSON, "r") as f:
            data = json.load(f)
            return data.get("file_id")
    return None

async def restore_from_last_backup():
    file_id = get_last_backup_file_id()
    if not file_id:
        return "No backup file ID found. Please perform a backup first."

    log.info(f"Restoring from backup file with ID: {file_id}")
    file_path = await app.download_media(file_id)
    response = restore_db(file_path)
    os.remove(file_path)
    return response

if __name__ == "__main__":
    load_all_modules()

    try:
        app.start()
        telebot.start(bot_token=config.BOT_TOKEN)
        initialize_services()
        ensure_owner_is_hokage()
        edit_restart_message()
        clear_downloads_folder()
        notify_startup()

        loop = asyncio.get_event_loop()

        async def initialize_async_components():
            await setup_indexes()
            if await is_database_empty():
                log.warning("Database is empty. Attempting to restore from the last backup...")
                # try :
                #     restore_status = await restore_from_last_backup()
                #     log.info(restore_status)
                # except:
                #     pass
            else:
                log.info("Database is not empty. Proceeding with startup.")
            scheduler.start()
            log.info("Async components initialized.")

            bot_details = await app.get_me()
            log.info(f"Bot Configured: Name: {bot_details.first_name}, ID: {bot_details.id}, Username: @{bot_details.username}")

        loop.run_until_complete(initialize_async_components())
        ptb.run_polling(timeout=15, drop_pending_updates=True)
        log.info("Bot started. Press Ctrl+C to stop.")
        idle()

    except Exception as e:
        log.exception(e)
