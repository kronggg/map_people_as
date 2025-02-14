from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

KEY = os.getenv("ENCRYPTION_KEY")
cipher = Fernet(KEY)

def encrypt_data(data: str) -> bytes:
    return cipher.encrypt(data.encode())


def decrypt_data(encrypted_data: bytes) -> str:
    return cipher.decrypt(encrypted_data).decode()