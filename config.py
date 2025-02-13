import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

class Config:
    # Telegram
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    # Database
    DB_NAME = os.getenv("DB_NAME", "users.db")
    
    # Security
    CIPHER_KEY = Fernet.generate_key()
    OTP_TIMEOUT = 300
    
    # States
    (
        GDPR_CONSENT,
        PHONE_INPUT,
        OTP_VERIFICATION,
        FULL_NAME,
        CITY,
        CONNECTIONS,
        MAIN_MENU,
        PROFILE_EDITING,
        SEARCH_FILTERS,
        SEARCH_LOCATION_INPUT,
        SEARCH_SKILLS_INPUT,
        SEARCH_RESULTS,
        VIEW_PROFILE,
        PROFILE_EDITING_NAME,
        PROFILE_EDITING_CITY
    ) = range(15)
    
    # Texts
    GDPR_TEXT = """📜 *GDPR-соглашение*
    
Ваши данные будут использоваться исключительно для:
- Поиска профессиональных связей
- Персонализации сервиса
- Обеспечения безопасности аккаунта"""
    
    # Geocoding
    GEOCODING_LANGUAGE = "ru"
    SEARCH_RADIUS = 50
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
