import pyotp
from datetime import datetime, timedelta
from config import Config

class OTPService:
    @classmethod
    def generate_otp(cls, user_id: int) -> tuple:
        """Генерирует OTP с привязкой к пользователю и времени"""
        secret = pyotp.random_base32()
        valid_until = datetime.now() + timedelta(seconds=Config.OTP_TIMEOUT)
        otp = pyotp.TOTP(secret).now()
        return otp, secret, valid_until

    @classmethod
    def verify_otp(cls, secret: str, code: str) -> bool:
        """Проверяет OTP с расширенным временным окном"""
        totp = pyotp.TOTP(secret)
        return totp.verify(
            code, 
            valid_window=2,  # ±1 интервал (всего 3 периода по 30 сек)
            after=datetime.now() - timedelta(seconds=90)
        )