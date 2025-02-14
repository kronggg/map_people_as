from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from config import Config
from database.core import DatabaseManager
from utils.localization import translate
import logging

logger = logging.getLogger(__name__)

class SearchMenu:
    @staticmethod
    async def show_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text(translate("search_prompt", context.user_data.get("language", Config.DEFAULT_LANGUAGE)))
        return Config.SEARCH_FILTERS

    @staticmethod
    async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query.data
        results = await DatabaseManager.fetch(
            """SELECT * FROM users 
            WHERE city LIKE ? OR skills LIKE ? OR hobbies LIKE ?""",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        
        if not results:
            await update.callback_query.edit_message_text(translate("no_results", context.user_data.get("language", Config.DEFAULT_LANGUAGE)))
            return Config.SEARCH_RESULTS

        keyboard = [
            [InlineKeyboardButton(f"{row['full_name']} ({row['city']})", callback_data=f"view_profile_{row['user_id']}")]
            for row in results
        ]
        
        await update.callback_query.edit_message_text(
            translate("search_results", context.user_data.get("language", Config.DEFAULT_LANGUAGE)),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return Config.SEARCH_RESULTS

    @classmethod
    def get_conversation_handler(cls):
        return ConversationHandler(
            entry_points=[CallbackQueryHandler(cls.show_search, pattern="^menu_search$")],
            states={
                Config.SEARCH_FILTERS: [CallbackQueryHandler(cls.handle_search)],
                Config.SEARCH_RESULTS: [CallbackQueryHandler(cls.handle_search, pattern="^view_profile_")]
            },
            fallbacks=[CallbackQueryHandler(lambda u,c: ConversationHandler.END, pattern="^cancel$")],
            per_message=True
        )