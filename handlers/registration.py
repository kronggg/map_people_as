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
from utils.database import DatabaseManager

# Состояния для ConversationHandler
(
    GDPR_CONSENT,
    ENTER_FULL_NAME,
    ENTER_NICKNAME,
    ENTER_PHONE,
    VERIFY_OTP,
    ENTER_LOCATION,
    ENTER_PROFESSION,
    ENTER_SKILLS,
    ENTER_HOBBIES,
) = range(9)

# Валидация данных
def validate_phone(phone: str) -> bool:
    pattern = r"^\+7\d{10}$"
    return re.match(pattern, phone) is not None


def validate_full_name(name: str) -> bool:
    return len(name.split()) >= 2


def validate_nickname(nickname: str) -> bool:
    return len(nickname) >= 3


# Генерация OTP
def generate_otp_secret():
    return pyotp.random_base32()


# Обработчики
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("✅ Согласиться", callback_data="gdpr_agree")],
        [InlineKeyboardButton("❌ Отказаться", callback_data="gdpr_decline")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Политика конфиденциальности...", reply_markup=reply_markup)
    return GDPR_CONSENT


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
        await query.edit_message_text("Теперь введите ваше ФИО:")
        return ENTER_FULL_NAME
    else:
        await query.answer("Вы отказались от регистрации.")
        await query.edit_message_text("Регистрация отменена.")
        return ConversationHandler.END


async def enter_full_name(update: Update, context: CallbackContext):
    full_name = update.message.text
    if validate_full_name(full_name):
        context.user_data["full_name"] = full_name
        await update.message.reply_text("Введите ваш никнейм:")
        return ENTER_NICKNAME
    else:
        await update.message.reply_text("Неверный формат ФИО. Попробуйте снова.")
        return ENTER_FULL_NAME


async def enter_nickname(update: Update, context: CallbackContext):
    nickname = update.message.text
    if validate_nickname(nickname):
        context.user_data["nickname"] = nickname
        await update.message.reply_text("Введите ваш номер телефона (в формате +79991234567):")
        return ENTER_PHONE
    else:
        await update.message.reply_text("Никнейм должен содержать минимум 3 символа.")
        return ENTER_NICKNAME


async def enter_phone(update: Update, context: CallbackContext):
    phone = update.message.text
    if validate_phone(phone):
        context.user_data["phone"] = phone
        otp_secret = generate_otp_secret()
        context.user_data["otp_secret"] = otp_secret
        totp = pyotp.TOTP(otp_secret)
        otp_code = totp.now()
        await update.message.reply_text(f"Ваш код подтверждения: {otp_code}")
        await update.message.reply_text("Введите код подтверждения:")
        return VERIFY_OTP
    else:
        await update.message.reply_text("Неверный формат телефона. Введите в формате +79991234567.")
        return ENTER_PHONE


async def verify_otp(update: Update, context: CallbackContext):
    user_code = update.message.text
    otp_secret = context.user_data.get("otp_secret")
    if otp_secret and pyotp.TOTP(otp_secret).verify(user_code):
        await update.message.reply_text("Код подтверждён! Теперь введите вашу страну:")
        return ENTER_LOCATION
    else:
        await update.message.reply_text("Неверный код. Попробуйте ещё раз.")
        return VERIFY_OTP


async def enter_location(update: Update, context: CallbackContext):
    context.user_data["country"] = update.message.text
    await update.message.reply_text("Введите ваш регион (область, штат и т.д.):")
    return ENTER_LOCATION


async def enter_region(update: Update, context: CallbackContext):
    context.user_data["region"] = update.message.text
    await update.message.reply_text("Введите ваш город:")
    return ENTER_CITY


async def enter_city(update: Update, context: CallbackContext):
    city = update.message.text
    coordinates = geocode_city(city)
    if coordinates:
        context.user_data["latitude"], context.user_data["longitude"] = coordinates
        await update.message.reply_text("Город распознан! Теперь укажите вашу профессию:")
        return ENTER_PROFESSION
    else:
        await update.message.reply_text("Не удалось распознать город. Попробуйте ещё раз.")
        return ENTER_CITY


async def enter_profession(update: Update, context: CallbackContext):
    context.user_data["profession"] = update.message.text
    await update.message.reply_text("Теперь укажите ваши навыки:")
    return ENTER_SKILLS


async def enter_skills(update: Update, context: CallbackContext):
    context.user_data["skills"] = update.message.text
    await update.message.reply_text("Теперь укажите ваши хобби:")
    return ENTER_HOBBIES


async def enter_hobbies(update: Update, context: CallbackContext):
    context.user_data["hobbies"] = update.message.text
    user_id = update.message.from_user.id
    await DatabaseManager.execute(
        """
        INSERT INTO users (
            user_id, full_name, nickname, phone, country, region, city, latitude, longitude,
            profession, skills, hobbies, consent_status, data_expiry, otp_secret
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, DATE('now', '+2 years'), ?)
        """,
        (
            user_id,
            context.user_data["full_name"],
            context.user_data["nickname"],
            context.user_data["phone"],
            context.user_data["country"],
            context.user_data["region"],
            context.user_data["city"],
            context.user_data["latitude"],
            context.user_data["longitude"],
            context.user_data["profession"],
            context.user_data["skills"],
            context.user_data["hobbies"],
            context.user_data["otp_secret"],
        ),
    )
    await update.message.reply_text("Регистрация завершена! Теперь вы можете использовать бота.")
    return ConversationHandler.END


# Создание ConversationHandler
def get_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GDPR_CONSENT: [CallbackQueryHandler(handle_gdpr_choice)],
            ENTER_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_full_name)],
            ENTER_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_nickname)],
            ENTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_phone)],
            VERIFY_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_otp)],
            ENTER_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_location)],
            ENTER_PROFESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_profession)],
            ENTER_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_skills)],
            ENTER_HOBBIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_hobbies)],
        },
        fallbacks=[],
    )
