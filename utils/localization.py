from config import Config

translations = {
    "ru": {
        "GDPR_TEXT": "Ваши данные будут использоваться исключительно для...",
        "accept_button": "✅ Принять",
        "enter_phone": "📱 Введите ваш телефон в международном формате:",
        "invalid_phone_format": "❌ Неверный формат телефона. Пример: +79991234567",
        "enter_otp": "🔐 Ваш код подтверждения: {otp_code}\nВведите его ниже:",
        "invalid_otp": "🚫 Неверный код. Попробуйте еще раз.",
        "enter_full_name": "📝 Введите ваше полное имя:",
        "invalid_full_name": "❌ Введите имя и фамилию через пробел.",
        "enter_city": "🌍 Введите ваш город или отправьте геолокацию:",
        "geocoding_error": "❌ Ошибка определения локации: {error}",
        "registration_complete": "🎉 Регистрация завершена! Используйте /menu для доступа к функциям.",
        "registration_error": "🚨 Произошла ошибка, попробуйте позже.",
        "main_menu_button": "🏠 Главное меню"
    },
    "en": {
        "GDPR_TEXT": "Your data will be used exclusively for...",
        "accept_button": "✅ Accept",
        "enter_phone": "📱 Enter your phone number in international format:",
        "invalid_phone_format": "❌ Invalid phone format. Example: +79991234567",
        "enter_otp": "🔐 Your verification code: {otp_code}\nEnter it below:",
        "invalid_otp": "🚫 Invalid code. Please try again.",
        "enter_full_name": "📝 Enter your full name:",
        "invalid_full_name": "❌ Please enter your first and last name separated by a space.",
        "enter_city": "🌍 Enter your city or send your location:",
        "geocoding_error": "❌ Location error: {error}",
        "registration_complete": "🎉 Registration complete! Use /menu to access features.",
        "registration_error": "🚨 An error occurred, please try again later.",
        "main_menu_button": "🏠 Main Menu"
    }
}

def translate(key: str, language: str = Config.DEFAULT_LANGUAGE):
    """Перевод текста на выбранный язык"""
    return translations.get(language, translations[Config.DEFAULT_LANGUAGE]).get(key, key)