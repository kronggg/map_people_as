from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext
from utils.database.core import DatabaseManager

async def show_menu(update: Update, context: CallbackContext):
    cursor = DatabaseManager.cursor
    cursor.execute("SELECT COUNT(*) FROM users WHERE consent_status = 1")
    user_count = cursor.fetchone()[0]

    lang = context.user_data.get("language", "RU")
    if lang == "RU":
        menu_text = f"Главное меню:\n\nВсего зарегистрировано пользователей: {user_count}"
    else:
        menu_text = f"Main menu:\n\nTotal registered users: {user_count}"

    keyboard = [
        [InlineKeyboardButton("🗺️ Карта пользователей", callback_data="map")],
        [InlineKeyboardButton("🔍 Поиск по критериям", callback_data="search_criteria")],
        [InlineKeyboardButton("📄 Мои данные", callback_data="my_data")],
        [InlineKeyboardButton("🚫 Отозвать согласие", callback_data="revoke_consent")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(menu_text, reply_markup=reply_markup)

def get_menu_handler():
    return CommandHandler("menu", show_menu)