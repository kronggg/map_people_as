import phonenumbers
from config import Config

class Security:
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Валидация международного номера телефона"""
        try:
            parsed_number = phonenumbers.parse(phone, None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.NumberParseException:
            return False