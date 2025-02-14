from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
)
import re
import pyotp
from utils.geocoder import geocode_city
from utils.database.core import DatabaseManager
from datetime import datetime

# Состояния
(
    GDPR_CONSENT,
    CHOOSE_LANGUAGE,
    ENTER_FULL_NAME,
    ENTER_NICKNAME,
    ENTER_PHONE,
    VERIFY_OTP,
    ENTER_LOCATION,
    ENTER_PROFESSION,
    ENTER_SKILLS,
    ENTER_HOBBIES,
) = range(10)

# Валидация данных
def validate_phone(phone: str) -> bool:
    pattern = r"^\+\d{1,3}\d{10}$"
    return re.match(pattern, phone) is not None


def validate_full_name(name: str) -> bool:
    return len(name.split()) >= 2


def validate_nickname(nickname: str) -> bool:
    return len(nickname) >= 3


# Генерация OTP
def generate_otp_secret():
    return pyotp.random_base32()


# Обработчики
class RegistrationHandlers:
    @staticmethod
    async def start(update: Update, context: CallbackContext):
        keyboard = [
            [InlineKeyboardButton("✅ Согласиться", callback_data="gdpr_agree")],
            [InlineKeyboardButton("❌ Отказаться", callback_data="gdpr_decline")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Политика конфиденциальности...", reply_markup=reply_markup)
        return GDPR_CONSENT

    @staticmethod
    async def handle_gdpr_choice(update: Update, context: CallbackContext):
        query = update.callback_query
        user_id = query.from_user.id
        if query.data == "gdpr_agree":
            consent_date = datetime.now().strftime("%Y-%m-%d")
            policy_version = "1.0"
            await DatabaseManager.execute(
                """
                INSERT INTO gdpr_consents (user_id, consent_date, policy_version)
                VALUES (?, ?, ?)
                """,
                (user_id, consent_date, policy_version),
            )
            await query.answer("Спасибо за согласие!")
            await query.edit_message_text("Выберите язык (RU/EN):")
            return CHOOSE_LANGUAGE
        else:
            await query.answer("Вы отказались от регистрации.")
            await query.edit_message_text("Регистрация отменена.")
            return ConversationHandler.END

    @staticmethod
    async def choose_language(update: Update, context: CallbackContext):
        language = update.message.text.upper()
        if language in ["RU", "EN"]:
            context.user_data["language"] = language
            await update.message.reply_text("Введите ваше ФИО:")
            return ENTER_FULL_NAME
        else:
            await update.message.reply_text("Неверный выбор языка. Выберите RU или EN.")
            return CHOOSE_LANGUAGE

    @staticmethod
    async def enter_full_name(update: Update, context: CallbackContext):
        full_name = update.message.text
        if validate_full_name(full_name):
            context.user_data["full_name"] = full_name
            await update.message.reply_text("Введите ваш никнейм:")
            return ENTER_NICKNAME
        else:
            await update.message.reply_text("Неверный формат ФИО. Попробуйте снова.")
            return ENTER_FULL_NAME

    # Продолжение обработчиков...

    @staticmethod
    def get_conversation_handler():
        return ConversationHandler(
            entry_points=[CommandHandler("start", RegistrationHandlers.start)],
            states={
                GDPR_CONSENT: [CallbackQueryHandler(RegistrationHandlers.handle_gdpr_choice)],
                CHOOSE_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, RegistrationHandlers.choose_language)],
                ENTER_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, RegistrationHandlers.enter_full_name)],
                # ... остальные состояния ...
            },
            fallbacks=[],
        )