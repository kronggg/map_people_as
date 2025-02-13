import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

class Config:
    """Класс конфигурации приложения"""
    
    # ======================
    #  Настройки Telegram
    # ======================
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    # ======================
    #  Настройки базы данных
    # ======================
    DB_NAME = os.getenv("DB_NAME", "users.db")
    SQL_ECHO = False  # Логирование SQL-запросов
    
    # ======================
    #  Безопасность
    # ======================
    CIPHER_KEY = Fernet.generate_key()
    OTP_TIMEOUT = 300  # 5 минут
    
    # ======================
    #  Состояния ConversationHandler
    # ======================
    (
        GDPR_CONSENT,       # 0 - Согласие с GDPR
        PHONE_INPUT,        # 1 - Ввод телефона
        OTP_VERIFICATION,   # 2 - Проверка OTP
        FULL_NAME,          # 3 - Ввод ФИО
        CITY,               # 4 - Ввод города
        CONNECTIONS,        # 5 - Управление связями
        MAIN_MENU,          # 6 - Главное меню
        PROFILE_EDITING,    # 7 - Редактирование профиля
        SEARCH_FILTERS,     # 8 - Выбор фильтров поиска
        SEARCH_LOCATION_INPUT,  # 9 - Ввод локации
        SEARCH_SKILLS_INPUT,    # 10 - Ввод навыков
        SEARCH_RESULTS,     # 11 - Результаты поиска
        VIEW_PROFILE,       # 12 - Просмотр профиля
        PROFILE_EDITING_NAME,   # 13 - Изменение имени
        PROFILE_EDITING_CITY,   # 14 - Изменение города
    ) = range(15)

    # ======================
    #  Тексты и сообщения
    # ======================
    GDPR_TEXT = """📜 *GDPR-соглашение*
    
Ваши данные будут использоваться исключительно для:
- Поиска профессиональных связей
- Персонализации сервиса
- Обеспечения безопасности аккаунта"""

    MENU_TEXTS = {
        'main': "🏠 *Главное меню*",
        'profile': "👤 *Ваш профиль*",
        'search': "🔍 *Поиск связей*",
        'connections': "📨 *Мои подключения*"
    }

    # ======================
    #  Геокодирование
    # ======================
    GEOCODING_LANGUAGE = "ru"  # Язык результатов
    SEARCH_RADIUS = 50  # Радиус поиска в км
    
    # ======================
    #  Redis и лимиты
    # ======================
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SEARCH_RESULTS_LIMIT = 50  # Макс. результатов поиска