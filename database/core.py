import aiosqlite
from config import Config

class DatabaseManager:
    @staticmethod
    async def execute(query: str, params: tuple = None):
        async with aiosqlite.connect(Config.DB_NAME) as db:
            await db.execute(query, params or ())
            await db.commit()

    @staticmethod
    async def fetch(query: str, params: tuple = None):
        async with aiosqlite.connect(Config.DB_NAME) as db:
            cursor = await db.execute(query, params or ())
            return await cursor.fetchall()

    @staticmethod
    async def fetch_one(query: str, params: tuple = None):
        async with aiosqlite.connect(Config.DB_NAME) as db:
            cursor = await db.execute(query, params or ())
            return await cursor.fetchone()