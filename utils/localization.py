from config import Config

translations = {
    "ru": {
        "main_menu_text": "🏠 Главное меню\n\n👤 Пользователей: {users}",
        "profile_button": "👤 Профиль",
        "search_button": "🔍 Поиск",
        "profile_text": "👤 Ваш профиль:\n\n📝 Имя: {name}\n📍 Город: {city}\n🛠 Навыки: {skills}\n🎯 Хобби: {hobbies}",
        "edit_profile_button": "✏️ Редактировать профиль",
        "search_prompt": "🔍 Введите навыки, город или хобби для поиска:",
        "no_results": "😞 Ничего не найдено.",
        "search_results": "🔎 Результаты поиска:"
    },
    "en": {
        "main_menu_text": "🏠 Main Menu\n\n👤 Users: {users}",
        "profile_button": "👤 Profile",
        "search_button": "🔍 Search",
        "profile_text": "👤 Your Profile:\n\n📝 Name: {name}\n📍 City: {city}\n🛠 Skills: {skills}\n🎯 Hobbies: {hobbies}",
        "edit_profile_button": "✏️ Edit Profile",
        "search_prompt": "🔍 Enter skills, city, or hobbies to search:",
        "no_results": "😞 No results found.",
        "search_results": "🔎 Search Results:"
    }
}

def translate(key: str, language: str = Config.DEFAULT_LANGUAGE):
    """Перевод текста на выбранный язык"""
    return translations.get(language, translations[Config.DEFAULT_LANGUAGE]).get(key, key)