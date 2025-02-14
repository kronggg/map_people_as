from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from config import Config
from database.core import DatabaseManager
from utils.localization import translate
import logging

logger = logging.getLogger(__name__)

class MainMenu:
    @staticmethod
    async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    @classmethod
    def get_conversation_handler(cls):
        return ConversationHandler(
            entry_points=[CallbackQueryHandler(cls.show_main_menu, pattern="^main_menu$")],
            states={
                Config.MAIN_MENU: [CallbackQueryHandler(cls.show_main_menu)]
            },
            fallbacks=[CallbackQueryHandler(lambda u,c: ConversationHandler.END, pattern="^cancel$")],  # Исправлено
            per_message=True
        )