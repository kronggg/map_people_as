from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import Config
from database.core import DatabaseManager
from utils.geocoder import Geocoder, GeocodingError
from utils.localization import translate

class SearchMenu:
    @staticmethod
    async def show_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отображение поиска"""
        await update.message.reply_text(translate("search_prompt", context.user_data.get("language", Config.DEFAULT_LANGUAGE)))
        return Config.SEARCH_FILTERS

    @staticmethod
    async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка поискового запроса"""
        query = update.message.text
        results = await DatabaseManager.fetch(
            """SELECT * FROM users 
            WHERE city LIKE ? OR skills LIKE ? OR hobbies LIKE ?""",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        
        if not results:
            await update.message.reply_text(translate("no_results", context.user_data.get("language", Config.DEFAULT_LANGUAGE)))
            return Config.SEARCH_RESULTS

        keyboard = [
            [InlineKeyboardButton(f"{row['full_name']} ({row['city']})", callback_data=f"view_profile_{row['user_id']}")]
            for row in results
        ]
        
        await update.message.reply_text(
            translate("search_results", context.user_data.get("language", Config.DEFAULT_LANGUAGE)),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return Config.SEARCH_RESULTS