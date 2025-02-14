from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import Config
from database.core import DatabaseManager
from utils.localization import translate

class ConnectionHandlers:
    @staticmethod
    async def init_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Инициирует процесс установки связи"""
        await update.message.reply_text(translate("connection_prompt", context.user_data.get("language", Config.DEFAULT_LANGUAGE)))
        return Config.CONNECTIONS

    @staticmethod
    async def handle_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запроса на связь"""
        query = update.callback_query
        await query.answer()
        
        target_user_id = int(query.data.split('_')[-1])
        initiator_id = query.from_user.id

        await DatabaseManager.execute(
            """INSERT INTO connections (user_from, user_to, status) VALUES (?, ?, 'pending')""",
            (initiator_id, target_user_id)
        )
        
        await query.edit_message_text(translate("connection_sent", context.user_data.get("language", Config.DEFAULT_LANGUAGE)))
        return ConversationHandler.END