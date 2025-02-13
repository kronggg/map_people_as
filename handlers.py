##############################################
# handlers.py - Основные обработчики
##############################################

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

class RegistrationHandlers:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start с проверкой регистрации"""
        user_id = update.effective_user.id
        
        if await Database.user_exists(user_id):
            await update.message.reply_text(
                "Вы уже зарегистрированы! Используйте /menu"
            )
            return
        
        # Показать GDPR и начать регистрацию
        keyboard = [
            [InlineKeyboardButton("✅ Согласиться", callback_data="gdpr_agree")],
            [InlineKeyboardButton("❌ Отказаться", callback_data="gdpr_decline")]
        ]
        await update.message.reply_text(
            Config.GDPR_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return Config.GDPR_CONSENT