import logging
from telegram.ext import Application
from config import Config
from handlers.registration import RegistrationHandlers
from handlers.menu.main import MainMenu
from database.core import DatabaseManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def init_database():
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
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")

def setup_handlers(app):
    try:
        app.add_handler(RegistrationHandlers.get_conversation_handler())
        app.add_handler(MainMenu.get_conversation_handler())
        logger.info("Handlers registered successfully")
    except Exception as e:
        logger.error(f"Handler setup failed: {str(e)}")

def main():
    try:
        app = Application.builder().token(Config.TOKEN).post_init(init_database).build()
        setup_handlers(app)
        app.run_polling()
    except Exception as e:
        logger.critical(f"Application failed: {str(e)}")

if __name__ == "__main__":
    main()