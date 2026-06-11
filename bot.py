import logging
import requests
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
)
from telegram.constants import ParseMode
from typing import Final
from telegram.ext import CallbackQueryHandler
from telegram.ext import MessageHandler, filters
from dotenv import load_dotenv
from telegram.ext import CommandHandler, MessageHandler, filters

load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# =========================
# 📦 YOUR DATA (UNCHANGED)
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
# 🧠 NAVIGATION STATE
# =========================

def set_nav(context, value):
    context.user_data["nav"] = value

def get_nav(context):
    return context.user_data.get("nav", "language")

# =========================
# ⬅️ BACK BUTTON
# =========================

def back_btn():
    return InlineKeyboardMarkup([
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
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("SV", callback_data="sv_eng"),
            InlineKeyboardButton("MEGA", callback_data="mega_eng"),
            InlineKeyboardButton("SWSH", callback_data="swsh_eng"),
        ]
    ])

def jap_era_menu():
    return InlineKeyboardMarkup([
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
# 🚀 ROUTES (MENUS)
# =========================

@route("Eng")
async def eng(update, context):
    set_nav(context, "language")
    await update.callback_query.edit_message_text(
        "Please choose your era:",
        reply_markup=eng_era_menu()
    )

@route("Jap")
async def jap(update, context):
    set_nav(context, "language")
    await update.callback_query.edit_message_text(
        "Please choose your era:",
        reply_markup=jap_era_menu()
    )

@route("sv_eng")
async def sv_eng(update, context):
    set_nav(context, "era_eng")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Show All", callback_data="sv_eng_all")],
        [InlineKeyboardButton("Surging Sparks", callback_data="ss_eng")],
        [InlineKeyboardButton("Prismatic Evolutions", callback_data="pris_eng")],
        [InlineKeyboardButton("Destined Rivals", callback_data="dr_eng")],
        [InlineKeyboardButton("Paradox Rift", callback_data="pr_eng")],
        [InlineKeyboardButton("Temporal Forces", callback_data="tf_sv_eng")],
        [InlineKeyboardButton("151", callback_data="151_eng")]
    ])

    await update.callback_query.edit_message_text(
        "Please choose a set:",
        reply_markup=keyboard
    )

@route("mega_jap")
async def mega_jap(update, context):
    set_nav(context, "era_jap")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Show All", callback_data="mega_jap_all")],
        [InlineKeyboardButton("Mega Dream", callback_data="md_jap")],
        [InlineKeyboardButton("Mega Symphonia", callback_data="ms_jap")],
        [InlineKeyboardButton("Mega Brave", callback_data="mb_jap")]
    ])

    await update.callback_query.edit_message_text(
        "Please choose a set:",
        reply_markup=keyboard
    )

# =========================
# 📦 SET + ERA CALLBACK MAPS
# =========================

SET_CALLBACKS = {
    "ss_eng": ("Surging Sparks", SVDIC_ENG["Sealed"]["Surging Sparks"]),
    "pris_eng": ("Prismatic Evolution", SVDIC_ENG["Sealed"]["Prismatic Evolution"]),
    "dr_eng": ("Destined Rivals", SVDIC_ENG["Sealed"]["Destined Rivals"]),
    "pr_eng": ("Paradox Rift", SVDIC_ENG["Sealed"]["Paradox Rift"]),
    "151_eng": ("151", SVDIC_ENG["Sealed"]["151"]),
    "tf_sv_eng": ("Temporal Forces", SVDIC_ENG["Sealed"]["Temporal Forces"]),

    "st_eng": ("Silver Tempest", SWSHDIC_ENG["SWSH"]["Sealed"]["Silver Tempest"]),
    "fs_eng": ("Fusion Strike", SWSHDIC_ENG["SWSH"]["Sealed"]["Fusion Strike"]),

    "ah_eng": ("Ascended Heros", MEGA_ENG["MEGA"]["Sealed"]["Ascended Heros"]),
    "pf_eng": ("Phantasmal Flames", MEGA_ENG["MEGA"]["Sealed"]["Phantasmal Flames"]),

    "bb_jap": ("Black Bolt", SVDIC_JAP["SV"]["Sealed"]["Black Bolt"]),
    "wf_jap": ("White Flare", SVDIC_JAP["SV"]["Sealed"]["White Flare"]),
    "gotr_jap": ("Glory of Team Rocket", SVDIC_JAP["SV"]["Sealed"]["GOTR"]),
    "tf_jap": ("Terrestrial Festival ex", SVDIC_JAP["SV"]["Sealed"]["TF"]),

    "md_jap": ("Mega Dream", MEGA_JAP["MEGA"]["Sealed"]["Mega Dream"]),
    "ms_jap": ("Mega Symphonia", MEGA_JAP["MEGA"]["Sealed"]["Mega Symphonia"]),
    "mb_jap": ("Mega Brave", MEGA_JAP["MEGA"]["Sealed"]["Mega Brave"]),
}
ERA_CALLBACKS = {
    "sv_eng_all": ("English SV", SVDIC_ENG["Sealed"]),
    "swsh_eng_all": ("English SWSH", SWSHDIC_ENG["SWSH"]["Sealed"]),
    "mega_eng_all": ("English MEGA", MEGA_ENG["MEGA"]["Sealed"]),
    "sv_jap_all": ("Japanese SV", SVDIC_JAP["SV"]["Sealed"]),
    "mega_jap_all": ("Japanese MEGA", MEGA_JAP["MEGA"]["Sealed"]),
}
ERA_PARENT = {
    "sv_eng_all":   "sv_eng",
    "swsh_eng_all": "swsh_eng",
    "mega_eng_all": "mega_eng",
    "sv_jap_all":   "sv_jap",
    "mega_jap_all": "mega_jap",
}

# =========================
# 🔙 BACK HANDLER
# =========================

async def handle_back(update, context):
    query = update.callback_query
    nav = get_nav(context)

    if nav == "era_view":
        last_era = context.user_data.get("last_era", "")
        parent = ERA_PARENT.get(last_era)
        if parent and parent in ROUTES:
            query.data = parent
            await ROUTES[parent](update, context)
            return
        # Fallback if something goes wrong
        await query.edit_message_text("Please choose your language:", reply_markup=language_menu())
        set_nav(context, "language")
        return

    if nav == "set_view":
        await query.edit_message_text(
            "Please choose a set:",
            reply_markup=eng_era_menu()
        )
        set_nav(context, "era_eng")
        return

    if nav == "era_eng":
        await query.edit_message_text(
            "Please choose your era:",
            reply_markup=eng_era_menu()
        )
        set_nav(context, "language")
        return

    if nav == "era_jap":
        await query.edit_message_text(
            "Please choose your era:",
            reply_markup=jap_era_menu()
        )
        set_nav(context, "language")
        return

# =========================
# 🎯 MAIN HANDLER (ONLY ENTRY POINT)
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    # BACK
    if data == "back":
        await handle_back(update, context)
        return

    # ROUTES (menus)
    if data in ROUTES:
        await ROUTES[data](update, context)
        return

    # SET VIEW
    if data in SET_CALLBACKS:
        set_name, set_data = SET_CALLBACKS[data]
        set_nav(context, "set_view")

        await query.edit_message_text(
            text=format_inventory(set_name, set_data),
            reply_markup=back_btn()
        )
        return

    # ERA VIEW
    if data in ERA_CALLBACKS:
        era_name, era_data = ERA_CALLBACKS[data]
        set_nav(context, "era_view")

        await query.edit_message_text(
            text=format_era_inventory(era_name, era_data),
            reply_markup=back_btn()
        )
        return

# =========================
# 🚀 START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_nav(context, "language")

    await update.message.reply_text(
        "Please Choose a language:",
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


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    print("Bot running...")
    app.run_polling()






