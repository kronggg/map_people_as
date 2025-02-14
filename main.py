import logging
from telegram.ext import Application, CommandHandler
from config import Config
from handlers.registration import RegistrationHandlers
from handlers.menu.main import MainMenu
from database.core import DatabaseManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def init_database(_):
    """Инициализация базы данных с корректной сигнатурой"""
    try:
        await DatabaseManager.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            phone_hash TEXT UNIQUE,
            full_name TEXT NOT NULL,
            city TEXT,
            lat REAL,
            lon REAL,
            language TEXT DEFAULT 'ru',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"DB init error: {str(e)}")

def setup_handlers(app):
    """Регистрация обработчиков"""
    try:
        # Регистрируем ConversationHandler
        app.add_handler(RegistrationHandlers.get_conversation_handler())
        
        # Регистрируем другие обработчики
        app.add_handler(MainMenu.get_conversation_handler())
        
        logger.info("Handlers registered")
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")

def main():
    """Точка входа"""
    try:
        app = Application.builder() \
            .token(Config.TOKEN) \
            .post_init(init_database) \
            .build()
        
        setup_handlers(app)
        app.run_polling()
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main()
