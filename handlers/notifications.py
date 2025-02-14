from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import Config
from database.core import DatabaseManager
from utils.localization import translate

class NotificationHandlers:
    @staticmethod
    async def handle_connection_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ответа на запрос связи"""
        query = update.callback_query
        await query.answer()
        
        action, initiator_id = query.data.split('_')[1:]
        target_user_id = query.from_user.id

        new_status = 'accepted' if action == 'accept' else 'rejected'
        await DatabaseManager.execute(
            """UPDATE connections SET status = ? WHERE user_from = ? AND user_to = ?""",
            (new_status, initiator_id, target_user_id)
        )
        
        await query.edit_message_text(translate(f"connection_{new_status}", context.user_data.get("language", Config.DEFAULT_LANGUAGE)))
        return ConversationHandler.END