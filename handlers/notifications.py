from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from config import Config
from database.core import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class NotificationHandlers:
    @staticmethod
    async def handle_connection_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ответа на запрос связи"""
        query = update.callback_query
        await query.answer()
        
        try:
            action, initiator_id = query.data.split('_')[1:]
            target_user_id = query.from_user.id
            
            new_status = 'accepted' if action == 'accept' else 'rejected'
            await DatabaseManager.execute(
                """UPDATE connections 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE user_from = ? AND user_to = ?""",
                (new_status, int(initiator_id), target_user_id)
            )

            status_text = "принял" if new_status == 'accepted' else "отклонил"
            try:
                await context.bot.send_message(
                    chat_id=int(initiator_id),
                    text=f"Пользователь @{query.from_user.username} {status_text} ваш запрос!"
                )
            except Exception as e:
                logger.error(f"Ошибка уведомления: {e}")

            await query.edit_message_text(f"✅ Статус обновлен: {new_status.capitalize()}")
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Ошибка обработки ответа: {e}")
            await query.edit_message_text("⚠️ Произошла ошибка, попробуйте позже")
            return ConversationHandler.END

    @classmethod
    def get_handlers(cls):
        return [
            CallbackQueryHandler(
                cls.handle_connection_response, 
                pattern=r"^conn_(accept|reject)_\d+$"
            )
        ]