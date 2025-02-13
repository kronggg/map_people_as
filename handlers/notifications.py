from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from database.user_repository import UserRepository

class NotificationHandlers:
    @staticmethod
    async def handle_connection_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает Accept/Reject запроса на связь"""
        query = update.callback_query
        action, initiator_id = query.data.split('_')
        target_user_id = query.from_user.id
        
        # Обновляем статус связи
        new_status = 'accepted' if action == 'accept' else 'rejected'
        await UserRepository.update_connection_status(
            user_from=int(initiator_id),
            user_to=target_user_id,
            status=new_status
        )
        
        # Уведомляем инициатора
        response_text = "✅ Связь установлена!" if action == 'accept' else "❌ Запрос отклонен"
        await context.bot.send_message(
            chat_id=int(initiator_id),
            text=f"Пользователь @{query.from_user.username} {response_text.lower()}"
        )
        
        await query.edit_message_text(response_text)
        return ConversationHandler.END