##############################################
# config.py - Настройки и конфигурация
##############################################

import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Загрузка переменных окружения
load_dotenv()

class Config:
    # Telegram
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    # Database
    DB_NAME = "gdpr_bot.db"
    
    # Security
    CIPHER_KEY = Fernet.generate_key()
    
    # Limits
    MAX_DAILY_UPDATES = 5
    OTP_TIMEOUT = 300  # 5 минут
    
    # Geolocation
    GEOCODE_SERVICE = "nominatim"  # openstreetmap
    GEOCODE_LIMIT = 1  # запросов/сек