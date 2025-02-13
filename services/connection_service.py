from database import UserRepository

class ConnectionService:
    @staticmethod
    async def create_connection(user_from: int, user_to: int) -> bool:
        """Создаёт запрос на связь"""
        if await UserRepository.check_existing_connection(user_from, user_to):
            return False
            
        async with aiosqlite.connect(Config.DB_NAME) as db:
            await db.execute('''
                INSERT INTO connections 
                (user_from, user_to, status) 
                VALUES (?, ?, 'pending')
            ''', (user_from, user_to))
            await db.commit()
        return True