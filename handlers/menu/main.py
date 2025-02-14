from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import Config
from database.core import DatabaseManager
from utils.localization import translate

class MainMenu:
    @staticmethod
    async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отображение главного меню"""
        user_count = await DatabaseManager.fetch_one("SELECT COUNT(*) FROM users")
        text = translate("main_menu_text", context.user_data.get("language", Config.DEFAULT_LANGUAGE)).format(users=user_count[0])
        
        keyboard = [
            [InlineKeyboardButton(translate("profile_button", context.user_data.get("language", Config.DEFAULT_LANGUAGE)), callback_data="menu_profile")],
            [InlineKeyboardButton(translate("search_button", context.user_data.get("language", Config.DEFAULT_LANGUAGE)), callback_data="menu_search")]
        ]
        
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return Config.MAIN_MENU