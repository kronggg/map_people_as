import phonenumbers
from cryptography.fernet import Fernet
from config import Config

class Security:
    cipher = Fernet(Config.CIPHER_KEY)

    @classmethod
    def encrypt(cls, data: str) -> bytes:
        """Шифрование данных"""
        return cls.cipher.encrypt(data.encode())

    @classmethod
    def decrypt(cls, encrypted_data: bytes) -> str:
        """Дешифрование данных"""
        return cls.cipher.decrypt(encrypted_data).decode()

    @staticmethod
    def validate_phone(number: str) -> bool:
        """Валидация международного номера телефона"""
        try:
            parsed_number = phonenumbers.parse(number, None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.NumberParseException:
            return False

    @staticmethod
    def get_hash(data: str) -> str:
        """Генерация SHA-256 хеша"""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()