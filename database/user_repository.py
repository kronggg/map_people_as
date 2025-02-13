from cryptography.fernet import InvalidToken
from utils.security import Security, OTPService

class UserRepository:
    async def create_user(self, user_data: dict) -> dict:
        """Создание пользователя с полной валидацией"""
        encrypted_phone = Security.encrypt(user_data['phone'])
        
        async with aiosqlite.connect(Config.DB_NAME) as db:
            # Проверка дублей через атомарную транзакцию
            await db.execute("BEGIN EXCLUSIVE")
            
            cursor = await db.execute('''
                SELECT 1 FROM users 
                WHERE phone_hash = ? OR user_id = ?
            ''', (Security.get_hash(user_data['phone']), user_data['user_id']))
            
            if await cursor.fetchone():
                await db.rollback()
                raise DuplicateUserError("User already exists")
            
            # Сохранение основных данных
            await db.execute('''
                INSERT INTO users (
                    user_id, phone_hash, country_code, 
                    full_name, latitude, longitude,
                    profession, skills, otp_secret
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['user_id'],
                Security.get_hash(user_data['phone']),
                user_data.get('country_code', ''),
                user_data['full_name'],
                user_data['latitude'],
                user_data['longitude'],
                user_data.get('profession', ''),
                ','.join(user_data.get('skills', [])),
                user_data['otp_secret']
            ))
            
            # Сохранение истории телефона
            await db.execute('''
                INSERT INTO phone_history (
                    user_id, old_phone, new_phone
                ) VALUES (?, ?, ?)
            ''', (
                user_data['user_id'],
                None,
                encrypted_phone
            ))
            
            await db.commit()
        
        return await self.get_user(user_data['user_id'])

    async def get_user(self, user_id: int) -> dict:
        """Получение пользователя с дешифровкой телефона"""
        async with aiosqlite.connect(Config.DB_NAME) as db:
            cursor = await db.execute('''
                SELECT *, 
                (SELECT new_phone FROM phone_history 
                 WHERE user_id = users.user_id 
                 ORDER BY changed_at DESC LIMIT 1) as encrypted_phone
                FROM users 
                WHERE user_id = ?
            ''', (user_id,))
            
            user = await cursor.fetchone()
            if not user:
                raise UserNotFoundError()
            
            try:
                phone = Security.decrypt(user['encrypted_phone'])
            except InvalidToken:
                raise DecryptionError("Phone number decryption failed")
            
            return {
                **user,
                'phone': phone,
                'skills': user['skills'].split(',') if user['skills'] else []
            }
            
            class UserRepository:
    @staticmethod
    async def search_users(search_term: str) -> list:
        """Поиск пользователей по навыкам"""
        async with aiosqlite.connect(Config.DB_NAME) as db:
            cursor = await db.execute('''
                SELECT user_id, full_name, nickname, skills 
                FROM users 
                WHERE skills LIKE ? 
                LIMIT 10
            ''', (f"%{search_term}%",))
            
            return [
                UserSearchResult(
                    user_id=row[0],
                    full_name=row[1],
                    nickname=row[2],
                    skills=row[3]
                ) for row in await cursor.fetchall()
            ]
            
            class UserRepository:
    @staticmethod
    async def check_existing_connection(user1: int, user2: int) -> bool:
        """Проверяет существующую связь между пользователями"""
        async with aiosqlite.connect(Config.DB_NAME) as db:
            cursor = await db.execute('''
                SELECT 1 FROM connections 
                WHERE (user_from = ? AND user_to = ?)
                OR (user_from = ? AND user_to = ?)
                AND status != 'rejected'
            ''', (user1, user2, user2, user1))
            
            return bool(await cursor.fetchone())
            
            class UserRepository:
    @staticmethod
    async def get_user_connections(user_id: int) -> list:
        """Получает активные связи пользователя"""
        async with aiosqlite.connect(Config.DB_NAME) as db:
            cursor = await db.execute('''
                SELECT 
                    u.user_id,
                    u.full_name,
                    u.nickname,
                    u.profession,
                    u.skills,
                    CASE 
                        WHEN c.user_from = ? THEN 'outgoing'
                        ELSE 'incoming'
                    END AS direction
                FROM connections c
                JOIN users u ON u.user_id = CASE 
                    WHEN c.user_from = ? THEN c.user_to 
                    ELSE c.user_from 
                END
                WHERE (c.user_from = ? OR c.user_to = ?)
                AND c.status = 'accepted'
                ORDER BY c.created_at DESC
            ''', (user_id, user_id, user_id, user_id))
            
            return [dict(row) for row in await cursor.fetchall()]
            
        class UserRepository:
    @staticmethod
    async def get_user_connections(user_id: int) -> list:
        """
        Получает активные связи пользователя с дополнительной метаинформацией
        
        Параметры:
            user_id (int): Идентификатор пользователя, для которого ищем связи
            
        Возвращает:
            list[dict]: Список соединений в формате:
                {
                    'user_id': int,       # ID связанного пользователя
                    'full_name': str,     # Полное имя
                    'nickname': str,      # Ник в Telegram
                    'profession': str,    # Профессия
                    'skills': str,        # Список навыков через запятую
                    'direction': str      'outgoing'|'incoming' - кто инициировал связь
                }
        """
        async with aiosqlite.connect(Config.DB_NAME) as db:
            # Выполняем сложный JOIN-запрос:
            # 1. Выбираем все связи где пользователь является участником
            # 2. Определяем направление связи (исходящая/входящая)
            # 3. Присоединяем данные связанного пользователя
            cursor = await db.execute('''
                SELECT 
                    u.user_id,
                    u.full_name,
                    u.nickname,
                    u.profession,
                    u.skills,
                    CASE 
                        WHEN c.user_from = ? THEN 'outgoing'
                        ELSE 'incoming'
                    END AS direction
                FROM connections c
                JOIN users u ON u.user_id = CASE 
                    WHEN c.user_from = ? THEN c.user_to 
                    ELSE c.user_from 
                END
                WHERE (c.user_from = ? OR c.user_to = ?)
                AND c.status = 'accepted'
                ORDER BY c.created_at DESC
            ''', (user_id, user_id, user_id, user_id))
            
            # Конвертируем результат в список словарей
            return [dict(row) for row in await cursor.fetchall()]    