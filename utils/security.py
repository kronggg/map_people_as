from config import Config
from cryptography.fernet import Fernet
import phonenumbers
import hashlib
import logging

logger = logging.getLogger(__name__)

class Security:
    """Класс для операций с безопасностью и шифрованием"""
    
    # Инициализация системы шифрования
    cipher_suite = Fernet(Config.CIPHER_KEY)

    @classmethod
    def encrypt(cls, data: str) -> bytes:
        """Шифрование строковых данных с использованием Fernet"""
        try:
            return cls.cipher_suite.encrypt(data.encode('utf-8'))
        except Exception as e:
            logger.error(f"Ошибка шифрования: {e}")
            raise

    @classmethod
    def decrypt(cls, encrypted_data: bytes) -> str:
        """Дешифрование данных в исходную строку"""
        try:
            return cls.cipher_suite.decrypt(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Ошибка дешифрования: {e}")
            raise

    @staticmethod
    def validate_phone(number: str) -> bool:
        """Валидация международного формата номера телефона"""
        try:
            parsed_number = phonenumbers.parse(number, None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.NumberParseException as e:
            logger.warning(f"Неверный формат телефона: {number} - {e}")
            return False

    @staticmethod
    def get_hash(data: str) -> str:
        """Генерация SHA-256 хеша для данных"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @classmethod
    def secure_phone(cls, phone: str) -> tuple:
        """Полная обработка номера телефона: хеширование и шифрование"""
        try:
            if not cls.validate_phone(phone):
                raise ValueError("Invalid phone number format")
            
            phone_hash = cls.get_hash(phone)
            encrypted_phone = cls.encrypt(phone)
            
            return phone_hash, encrypted_phone
            
        except Exception as e:
            logger.error(f"Ошибка обработки телефона: {e}")
            raise

    @staticmethod
    def validate_password(password: str) -> bool:
        """Валидация сложности пароля"""
        if len(password) < 8:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        return True