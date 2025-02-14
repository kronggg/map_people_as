from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")