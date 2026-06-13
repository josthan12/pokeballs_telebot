import logging
import os
import json

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
from telegram.error import Forbidden

load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = 888225106

# =========================
# 📦 DATA
# =========================

SWSHDIC_ENG = {
    'SWSH': {
        'Sealed': {
            'Fusion Strike': {'Fusion Strike PC ETB': 1},
            'Silver Tempest': {'Silver Tempest Sleeves': 4}
        },
        'Singles': {},
        'Slabs': {}
    }
}

SVDIC_ENG = {
    'Sealed': {
        'Surging Sparks': {'Surging Sparks ETB': 2},
        'Prismatic Evolution': {
            'Prismatic PC ETB': 2,
            'Prismatic SPC': 1,
            'Prismatic Booster Bundle': 20,
            'Prismatic ETB Sealed Case': 1,
            "Pristmatic 2 Pack": 1
        },
        "Destined Rivals": {"Destined Rivals ETB": 3},
        "Paradox Rift": {"Paradox Rift Sleeves": 4},
        "Temporal Forces": {"Temporal Forces Sleeves": 0},
        "151": {"151 Alazaham Box": 1}
    },
    'Singles': {},
    'Slabs': {}
}

MEGA_ENG = {
    'MEGA': {
        'Sealed': {
            "Ascended Heros": {
                'Ascended Heros PC ETB': 1,
                "Ascended Heros ETB": 3
            },
            "Phantasmal Flames": {
                "Phantasmal Flames SPC Sealed Case": 1
            }
        },
        'Singles': {},
        'Slabs': {}
    }
}

SVDIC_JAP = {
    'SV': {
        'Sealed': {
            "GOTR": {'GOTR BB': 3},
            "TF": {'TF BB': 4},
            "Black Bolt": {"BB Deluxe BB": 1},
            "White Flare": {"WF Deluxe BB": 1}
        },
        'Singles': {},
        'Slabs': {}
    }
}

MEGA_JAP = {
    'MEGA': {
        'Sealed': {
            "Mega Dream": {'Mega Dream BB': 4},
            "Mega Brave": {"Mega Brave BB": 1},
            "Mega Symphonia": {"Mega Symphonia BB": 1},
            "Others": {
                "Pokemon Centre Special Boxes(Hiroshima/Tohoku/Fukouka)": 2,
                "Mega Brave/Symphonia Box": 1
            }
        },
        'Singles': {},
        'Slabs': {}
    }
}

# =========================
# 📊 FORMATTING
# =========================

def format_inventory(set_name, set_data):
    lines = [f"=== {set_name} ===", ""]
    for item, qty in sorted(set_data.items()):
        lines.append(f"{item} - {qty}")
    return "\n".join(lines)

def format_era_inventory(era_name, era_data):
    lines = [f"=== {era_name} Inventory ===", ""]
    for set_name in sorted(era_data):
        lines.append(f"📦 {set_name}")
        for item, qty in sorted(era_data[set_name].items()):
            lines.append(f"• {item} - {qty}")
        lines.append("")
    return "\n".join(lines)

# =========================
# 🧠 NAVIGATION HISTORY STACK
# =========================

def push_nav(context, key):
    context.user_data.setdefault("nav_history", []).append(key)

def pop_nav(context):
    history = context.user_data.get("nav_history", [])
    return history.pop() if history else None

def clear_nav(context):
    context.user_data["nav_history"] = []

# =========================
# ⬅️ BACK BUTTON HELPERS
# =========================

def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data="back")]
    ])

def with_back(buttons):
    return InlineKeyboardMarkup(buttons + [
        [InlineKeyboardButton("⬅️ Back", callback_data="back")]
    ])

# =========================
# 🧭 MENUS
# =========================

def language_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("English", callback_data="Eng"),
            InlineKeyboardButton("Japanese", callback_data="Jap"),
        ]
    ])

def eng_era_menu():
    return with_back([
        [
            InlineKeyboardButton("SV", callback_data="sv_eng"),
            InlineKeyboardButton("MEGA", callback_data="mega_eng"),
            InlineKeyboardButton("SWSH", callback_data="swsh_eng"),
        ]
    ])

def jap_era_menu():
    return with_back([
        [
            InlineKeyboardButton("SV", callback_data="sv_jap"),
            InlineKeyboardButton("MEGA", callback_data="mega_jap"),
        ]
    ])

# =========================
# 🧭 ROUTER
# =========================

ROUTES = {}

def route(key):
    def wrapper(func):
        ROUTES[key] = func
        return func
    return wrapper

# =========================
# 🚀 ROUTES
# Each route pushes its OWN key before rendering,
# so Back can pop it and re-call this same route.
# =========================

@route("Eng")
async def eng(update, context):
    push_nav(context, "Eng")
    await update.callback_query.edit_message_text(
        "Please choose your era:",
        reply_markup=eng_era_menu()
    )

@route("Jap")
async def jap(update, context):
    push_nav(context, "Jap")
    await update.callback_query.edit_message_text(
        "Please choose your era:",
        reply_markup=jap_era_menu()
    )

@route("sv_eng")
async def sv_eng_route(update, context):
    push_nav(context, "sv_eng")
    keyboard = with_back([
        [InlineKeyboardButton("📋 Show All", callback_data="sv_eng_all")],
        [InlineKeyboardButton("Surging Sparks", callback_data="ss_eng")],
        [InlineKeyboardButton("Prismatic Evolutions", callback_data="pris_eng")],
        [InlineKeyboardButton("Destined Rivals", callback_data="dr_eng")],
        [InlineKeyboardButton("Paradox Rift", callback_data="pr_eng")],
        [InlineKeyboardButton("Temporal Forces", callback_data="tf_sv_eng")],
        [InlineKeyboardButton("151", callback_data="151_eng")],
    ])
    await update.callback_query.edit_message_text("Please choose a set:", reply_markup=keyboard)

@route("mega_eng")
async def mega_eng_route(update, context):
    push_nav(context, "mega_eng")
    keyboard = with_back([
        [InlineKeyboardButton("📋 Show All", callback_data="mega_eng_all")],
        [InlineKeyboardButton("Ascended Heros", callback_data="ah_eng")],
        [InlineKeyboardButton("Phantasmal Flames", callback_data="pf_eng")],
    ])
    await update.callback_query.edit_message_text("Please choose a set:", reply_markup=keyboard)

@route("swsh_eng")
async def swsh_eng_route(update, context):
    push_nav(context, "swsh_eng")
    keyboard = with_back([
        [InlineKeyboardButton("📋 Show All", callback_data="swsh_eng_all")],
        [InlineKeyboardButton("Fusion Strike", callback_data="fs_eng")],
        [InlineKeyboardButton("Silver Tempest", callback_data="st_eng")],
    ])
    await update.callback_query.edit_message_text("Please choose a set:", reply_markup=keyboard)

@route("sv_jap")
async def sv_jap_route(update, context):
    push_nav(context, "sv_jap")
    keyboard = with_back([
        [InlineKeyboardButton("📋 Show All", callback_data="sv_jap_all")],
        [InlineKeyboardButton("Black Bolt", callback_data="bb_jap")],
        [InlineKeyboardButton("White Flare", callback_data="wf_jap")],
        [InlineKeyboardButton("Terrestial Festival ex", callback_data="tf_jap")],
        [InlineKeyboardButton("Glory Of Team Rocket", callback_data="gotr_jap")],
    ])
    await update.callback_query.edit_message_text("Please choose a set:", reply_markup=keyboard)

@route("mega_jap")
async def mega_jap_route(update, context):
    push_nav(context, "mega_jap")
    keyboard = with_back([
        [InlineKeyboardButton("📋 Show All", callback_data="mega_jap_all")],
        [InlineKeyboardButton("Mega Dream", callback_data="md_jap")],
        [InlineKeyboardButton("Mega Symphonia", callback_data="ms_jap")],
        [InlineKeyboardButton("Mega Brave", callback_data="mb_jap")],
    ])
    await update.callback_query.edit_message_text("Please choose a set:", reply_markup=keyboard)

# =========================
# 📦 SET + ERA CALLBACK MAPS
# =========================

SET_CALLBACKS = {
    "ss_eng":     ("Surging Sparks",      SVDIC_ENG["Sealed"]["Surging Sparks"]),
    "pris_eng":   ("Prismatic Evolution", SVDIC_ENG["Sealed"]["Prismatic Evolution"]),
    "dr_eng":     ("Destined Rivals",     SVDIC_ENG["Sealed"]["Destined Rivals"]),
    "pr_eng":     ("Paradox Rift",        SVDIC_ENG["Sealed"]["Paradox Rift"]),
    "151_eng":    ("151",                 SVDIC_ENG["Sealed"]["151"]),
    "tf_sv_eng":  ("Temporal Forces",     SVDIC_ENG["Sealed"]["Temporal Forces"]),
    "st_eng":     ("Silver Tempest",      SWSHDIC_ENG["SWSH"]["Sealed"]["Silver Tempest"]),
    "fs_eng":     ("Fusion Strike",       SWSHDIC_ENG["SWSH"]["Sealed"]["Fusion Strike"]),
    "ah_eng":     ("Ascended Heros",      MEGA_ENG["MEGA"]["Sealed"]["Ascended Heros"]),
    "pf_eng":     ("Phantasmal Flames",   MEGA_ENG["MEGA"]["Sealed"]["Phantasmal Flames"]),
    "bb_jap":     ("Black Bolt",          SVDIC_JAP["SV"]["Sealed"]["Black Bolt"]),
    "wf_jap":     ("White Flare",         SVDIC_JAP["SV"]["Sealed"]["White Flare"]),
    "gotr_jap":   ("Glory of Team Rocket",SVDIC_JAP["SV"]["Sealed"]["GOTR"]),
    "tf_jap":     ("Terrestrial Festival ex", SVDIC_JAP["SV"]["Sealed"]["TF"]),
    "md_jap":     ("Mega Dream",          MEGA_JAP["MEGA"]["Sealed"]["Mega Dream"]),
    "ms_jap":     ("Mega Symphonia",      MEGA_JAP["MEGA"]["Sealed"]["Mega Symphonia"]),
    "mb_jap":     ("Mega Brave",          MEGA_JAP["MEGA"]["Sealed"]["Mega Brave"]),
}

ERA_CALLBACKS = {
    "sv_eng_all":   ("English SV",      SVDIC_ENG["Sealed"]),
    "swsh_eng_all": ("English SWSH",    SWSHDIC_ENG["SWSH"]["Sealed"]),
    "mega_eng_all": ("English MEGA",    MEGA_ENG["MEGA"]["Sealed"]),
    "sv_jap_all":   ("Japanese SV",     SVDIC_JAP["SV"]["Sealed"]),
    "mega_jap_all": ("Japanese MEGA",   MEGA_JAP["MEGA"]["Sealed"]),
}

# =========================
# 🔙 BACK HANDLER
# =========================

async def handle_back(update, context):
    query = update.callback_query
    prev = pop_nav(context)

    if prev is None:
        # Stack is empty — we're at or behind the language screen
        clear_nav(context)
        await query.edit_message_text(
            "Please choose your language:",
            reply_markup=language_menu()
        )
        return

    if prev in ROUTES:
        # Pop it again before calling the route, because the route will
        # push its own key when it renders — we don't want a duplicate.
        await ROUTES[prev](update, context)
        # The route just pushed `prev` again, which is correct —
        # the stack now reflects the screen we're on.
        return

    # Fallback
    clear_nav(context)
    await query.edit_message_text(
        "Please choose your language:",
        reply_markup=language_menu()
    )

# =========================
# 🎯 MAIN HANDLER
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back":
        # Pop twice: once to undo the current screen's push,
        # once to get the screen before it.
        pop_nav(context)  # discard current screen
        await handle_back(update, context)
        return

    if data in ROUTES:
        await ROUTES[data](update, context)
        return

    if data in SET_CALLBACKS:
        set_name, set_data = SET_CALLBACKS[data]
        # No push here — the set menu route already pushed itself.
        # Back will pop the set menu key and return there correctly.
        await query.edit_message_text(
            text=format_inventory(set_name, set_data),
            reply_markup=back_btn()
        )
        return

    if data in ERA_CALLBACKS:
        era_name, era_data = ERA_CALLBACKS[data]
        # Same — no push needed; set menu is already on the stack.
        await query.edit_message_text(
            text=format_era_inventory(era_name, era_data),
            reply_markup=back_btn()
        )
        return

# =========================
# 🚀 START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_nav(context)
    await update.message.reply_text(
        "Please choose a language:",
        reply_markup=language_menu()
    )

# =========================
# ❓ HELP COMMAND
# =========================

HELP_TEXT = """
👋 *Welcome to the Inventory Bot!*

Here's how to use this bot:

📌 *Commands*
- /start – Browse the inventory
- /help – Show this help message
- /subscribe – Subscribe to the newsletter
- /unsubscribe – Unsubscribe from the newsletter

📰 *Newsletter*
- Subscribe to get market updates and stock news directly from me
- Unsubscribe anytime, no questions asked

🗂 *How to Browse*
1. Use /start to begin
2. Choose a language (English / Japanese)
3. Choose an era (SV, SWSH, MEGA)
4. Choose a set or tap 📋 Show All
5. Use ⬅️ Back to go back anytime

📦 *What's Available*
- Sealed products (ETBs, Booster Bundles, etc.)
- More categories coming soon!

📩 *Interested in purchasing?*
Contact: @pokesunshine

⚠️ _Inventory is updated manually and may not reflect real-time stock._
"""

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")

# =========================
# 💬 UNKNOWN MESSAGE HANDLER
# =========================

async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /start to browse the inventory or /help for assistance."
    )

# =========================
# 📰 SUBSCRIBER HELPERS
# =========================
 
SUBSCRIBERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subscribers.json")
 
def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            return []
        data = json.loads(content)
    return data.get("subscribers", [])
 
def save_subscribers(subscribers):
    """Save subscriber list to JSON file."""
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump({"subscribers": subscribers}, f, indent=2)
 
# =========================
# 📰 NEWSLETTER COMMANDS
# =========================
 
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers = load_subscribers()
 
    if chat_id in subscribers:
        await update.message.reply_text("You're already subscribed to the newsletter! 📬")
        return
 
    subscribers.append(chat_id)
    save_subscribers(subscribers)
    await update.message.reply_text(
        "You're now subscribed to the newsletter! 🎉\n"
        "You'll receive updates and market thoughts directly here.\n\n"
        "Use /unsubscribe anytime to opt out."
    )
 
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers = load_subscribers()
 
    if chat_id not in subscribers:
        await update.message.reply_text("You're not currently subscribed. Use /subscribe to join!")
        return
 
    subscribers.remove(chat_id)
    save_subscribers(subscribers)
    await update.message.reply_text("You've been unsubscribed. Sorry to see you go! 👋\nUse /subscribe anytime to rejoin.")
 
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only you can broadcast
    if update.effective_chat.id != OWNER_ID:
        await update.message.reply_text("You are not authorised to use this command.")
        return
 
    # Must provide a message: /broadcast <your message here>
    if not context.args:
        await update.message.reply_text(
            "Please provide a message to broadcast.\n"
            "Usage: /broadcast <your message>"
        )
        return
 
    message = " ".join(context.args)
    subscribers = load_subscribers()
 
    if not subscribers:
        await update.message.reply_text("No subscribers yet!")
        return
 
    newsletter_text = (
        f"📬 *Pokesunshine Newsletter*\n\n"
        f"{message}\n\n"
        f"_To unsubscribe, send /unsubscribe_"
    )
 
    sent = 0
    removed = []
 
    for chat_id in subscribers:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=newsletter_text,
                parse_mode="Markdown"
            )
            sent += 1
        except Forbidden:
            # User has blocked the bot — remove them automatically
            removed.append(chat_id)
 
    # Clean up blocked users
    if removed:
        for chat_id in removed:
            subscribers.remove(chat_id)
        save_subscribers(subscribers)
 
    summary = f"✅ Broadcast sent to {sent} subscriber(s)."
    if removed:
        summary += f"\n🚫 Removed {len(removed)} blocked user(s) from the list."
 
    await update.message.reply_text(summary)
 
async def subscriber_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner-only command to check how many subscribers you have."""
    if update.effective_chat.id != OWNER_ID:
        await update.message.reply_text("You are not authorised to use this command.")
        return
 
    subscribers = load_subscribers()
    await update.message.reply_text(f"📊 You currently have {len(subscribers)} subscriber(s).")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("subscribers", subscriber_count))

    print("Bot running...")
    app.run_polling()