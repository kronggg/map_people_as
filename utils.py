##############################################
# utils.py - Вспомогательные функции
##############################################

import phonenumbers
from cryptography.fernet import Fernet
from config import Config

class Validation:
    @staticmethod
    def phone(number: str) -> bool:
        """Валидация международного номера телефона"""
        try:
            parsed = phonenumbers.parse(number, None)
            return phonenumbers.is_valid_number(parsed)
        except:
            return False

class Security:
    cipher = Fernet(Config.CIPHER_KEY)
    
    @classmethod
    def encrypt(cls, data: str) -> bytes:
        """Шифрование чувствительных данных"""
        return cls.cipher.encrypt(data.encode())
    
    @classmethod
    def decrypt(cls, encrypted_data: bytes) -> str:
        """Дешифрование данных"""
        return cls.cipher.decrypt(encrypted_data).decode()