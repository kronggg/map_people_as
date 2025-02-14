import logging
from telegram.ext import Application, CommandHandler, ConversationHandler
from handlers.registration import RegistrationHandlers
from handlers.menu import MenuHandlers
from handlers.search import SearchHandlers
from handlers.profile import ProfileHandlers
from handlers.language import LanguageHandlers
from utils.database.core import DatabaseManager
from utils.geocoder import Geocoder
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")]
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
async def init_database():
    await DatabaseManager.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            nickname TEXT,
            phone TEXT,
            country TEXT,
            region TEXT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            profession TEXT,
            skills TEXT,
            hobbies TEXT,
            consent_status BOOLEAN DEFAULT 0,
            data_expiry DATE,
            otp_secret TEXT,
            language TEXT DEFAULT 'RU'
        )
    """)
    # ... другие таблицы ...
    logger.info("Database initialized successfully")

# Регистрация обработчиков
def setup_handlers(app: Application):
    app.add_handler(RegistrationHandlers.get_conversation_handler())
    app.add_handler(MenuHandlers.get_menu_handler())
    app.add_handler(ProfileHandlers.get_profile_handler())
    app.add_handler(SearchHandlers.get_search_handler())
    app.add_handler(LanguageHandlers.get_language_handler())

    # Общие команды
    app.add_handler(CommandHandler("start", RegistrationHandlers.start))
    app.add_handler(CommandHandler("help", MenuHandlers.help_command))

# Пост-инициализация
async def post_init(app: Application):
    await init_database()
    await Geocoder.warmup()
    logger.info("Application initialized successfully")

# Точка входа
def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set!")

    application = Application.builder().token(TOKEN).post_init(post_init).build()
    setup_handlers(application)
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()