from config import Config

translations = {
    "ru": {
        "GDPR_TEXT": "Ваши данные будут использоваться...",
        "accept_button": "✅ Принять",
        "invalid_phone_format": "❌ Неверный формат телефона",
        "enter_otp": "🔐 Введите код из SMS:"
    },
    "en": {
        "GDPR_TEXT": "Your data will be used...",
        "accept_button": "✅ Accept",
        "invalid_phone_format": "❌ Invalid phone format",
        "enter_otp": "🔐 Enter the SMS code:"
    }
}

def translate(key: str, language: str = Config.DEFAULT_LANGUAGE):
    """Перевод текста на выбранный язык"""
    return translations.get(language, translations[Config.DEFAULT_LANGUAGE]).get(key, key)