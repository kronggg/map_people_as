import sqlite3

class DatabaseManager:
    conn = sqlite3.connect("gdpr_bot.db", check_same_thread=False)
    cursor = conn.cursor()

    @classmethod
    async def execute(cls, query, params=None):
        if params:
            cls.cursor.execute(query, params)
        else:
            cls.cursor.execute(query)
        cls.conn.commit()

    @classmethod
    async def fetch_all(cls, query, params=None):
        if params:
            cls.cursor.execute(query, params)
        else:
            cls.cursor.execute(query)
        return cls.cursor.fetchall()

    @classmethod
    async def fetch_one(cls, query, params=None):
        if params:
            cls.cursor.execute(query, params)
        else:
            cls.cursor.execute(query)
        return cls.cursor.fetchone()