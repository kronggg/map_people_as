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
    OTP_TIMEOUT = 300  # 5 минут
    
    # Localization
    DEFAULT_LANGUAGE = "ru"  # ru / en
    
    # OSM
    OSM_NOMINATIM_URL = os.getenv("OSM_NOMINATIM_URL", "https://nominatim.openstreetmap.org")
    
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
        VIEW_PROFILE
    ) = range(13)