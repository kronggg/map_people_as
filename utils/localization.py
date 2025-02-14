from config import Config
import logging

logger = logging.getLogger(__name__)

translations = {
    "ru": {
        "GDPR_TEXT": "🔒 Для продолжения необходимо принять нашу политику конфиденциальности...",
        "accept_button": "✅ Я принимаю условия",
        "gdpr_error": "❌ Для продолжения необходимо принять условия",
        "enter_phone": "📱 Введите номер телефона в формате +7XXXXXXXXXX:",
        "invalid_phone_format": "❌ Неверный формат номера",
        "enter_otp": "🔑 Введите полученный код: {otp_code}",
        "invalid_otp": "❌ Неверный код подтверждения",
        "enter_full_name": "👤 Введите ваше полное имя (Имя Фамилия):",
        "invalid_full_name": "❌ Требуется ввести имя и фамилию",
        "enter_city": "🌍 Введите ваш город или отправьте геолокацию:",
        "geocoding_error": "❌ Ошибка определения местоположения: {error}",
        "registration_complete": "🎉 Регистрация успешно завершена!",
        "registration_error": "⛔ Произошла ошибка при регистрации"
    },
    "en": {
        "GDPR_TEXT": "🔒 You must accept our privacy policy to continue...",
        "accept_button": "✅ I accept the terms",
        "gdpr_error": "❌ You must accept the terms to continue",
        "enter_phone": "📱 Enter phone number in +XXXXXXXXXXX format:",
        "invalid_phone_format": "❌ Invalid phone format",
        "enter_otp": "🔑 Enter verification code: {otp_code}",
        "invalid_otp": "❌ Invalid verification code",
        "enter_full_name": "👤 Enter your full name (First Last):",
        "invalid_full_name": "❌ Please enter first and last name",
        "enter_city": "🌍 Enter your city or share location:",
        "geocoding_error": "❌ Location error: {error}",
        "registration_complete": "🎉 Registration completed!",
        "registration_error": "⛔ Registration failed"
    }
}

def translate(key: str, language: str = Config.DEFAULT_LANGUAGE) -> str:
    try:
        lang_dict = translations.get(language, translations[Config.DEFAULT_LANGUAGE])
        return lang_dict[key]
    except KeyError as e:
        logger.error(f"Missing translation key: {str(e)}")
        return f"[{key}]"
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return "⚠️ System error"