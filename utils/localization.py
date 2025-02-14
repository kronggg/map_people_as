from config import Config
import logging

logger = logging.getLogger(__name__)

translations = {
    "ru": {
        "GDPR_TEXT": "🔒 Пожалуйста, ознакомьтесь с нашей политикой конфиденциальности...",
        "accept_button": "✅ Принять условия",
        "gdpr_error": "❌ Сначала примите условия использования",
        "enter_phone": "📱 Введите номер телефона в формате +79991234567:",
        "invalid_phone_format": "❌ Неверный формат телефона",
        "enter_otp": "🔑 Введите код подтверждения: {otp_code}",
        "invalid_otp": "❌ Неверный код подтверждения",
        "enter_full_name": "👤 Введите ваше полное имя:",
        "invalid_full_name": "❌ Введите имя и фамилию",
        "enter_city": "🌍 Введите ваш город или отправьте геолокацию:",
        "geocoding_error": "❌ Ошибка определения местоположения: {error}",
        "registration_complete": "🎉 Регистрация завершена!",
        "registration_error": "⛔ Ошибка регистрации"
    },
    "en": {
        "GDPR_TEXT": "🔒 Please read our privacy policy...",
        "accept_button": "✅ Accept terms",
        "gdpr_error": "❌ Please accept the terms first",
        "enter_phone": "📱 Enter phone number in +1234567890 format:",
        "invalid_phone_format": "❌ Invalid phone format",
        "enter_otp": "🔑 Enter verification code: {otp_code}",
        "invalid_otp": "❌ Invalid verification code",
        "enter_full_name": "👤 Enter your full name:",
        "invalid_full_name": "❌ Please enter first and last name",
        "enter_city": "🌍 Enter your city or share location:",
        "geocoding_error": "❌ Location error: {error}",
        "registration_complete": "🎉 Registration complete!",
        "registration_error": "⛔ Registration failed"
    }
}

def translate(key: str, language: str = Config.DEFAULT_LANGUAGE) -> str:
    try:
        return translations.get(language, translations[Config.DEFAULT_LANGUAGE])[key]
    except KeyError as e:
        logger.error(f"Missing translation: {str(e)}")
        return f"[{key}]"