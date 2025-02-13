##############################################
# database.py - Работа с базой данных
##############################################

import aiosqlite
from config import Config

class Database:
    @staticmethod
    async def init_db():
        """Инициализация таблиц в базе данных"""
        async with aiosqlite.connect(Config.DB_NAME) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    phone_hash TEXT UNIQUE,
                    country_code TEXT,
                    full_name TEXT,
                    nickname TEXT,
                    profession TEXT,
                    skills TEXT,
                    hobbies TEXT,
                    latitude REAL,
                    longitude REAL,
                    consent_status BOOLEAN DEFAULT 0,
                    data_expiry DATE,
                    otp_secret TEXT
                )''')
            
            # Остальные таблицы...
            
            await db.commit()

    @staticmethod
    async def user_exists(user_id: int):
        """Проверка существования пользователя"""
        async with aiosqlite.connect(Config.DB_NAME) as db:
            cursor = await db.execute(
                "SELECT 1 FROM users WHERE user_id = ?", 
                (user_id,)
            )
            return bool(await cursor.fetchone())