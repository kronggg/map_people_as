import logging
from telegram.ext import Application
from config import Config
from handlers.registration import RegistrationHandlers
from handlers.menu.main import MainMenu
from handlers.menu.profile import ProfileMenu
from handlers.menu.search import SearchMenu
from handlers.connections import ConnectionHandlers
from handlers.notifications import NotificationHandlers
from database.core import DatabaseManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def init_database():
    """Инициализация базы данных"""
    await DatabaseManager.execute(
        """CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            phone_hash TEXT UNIQUE,
            full_name TEXT NOT NULL,
            city TEXT,
            lat REAL,
            lon REAL,
            skills TEXT,
            hobbies TEXT,
            language TEXT DEFAULT 'ru',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    await DatabaseManager.execute(
        """CREATE TABLE IF NOT EXISTS connections (
            connection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_from INTEGER NOT NULL,
            user_to INTEGER NOT NULL,
            status TEXT CHECK(status IN ('pending', 'accepted', 'rejected')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )

def setup_handlers(app):
    """Регистрация всех обработчиков"""
    app.add_handler(RegistrationHandlers.get_conversation_handler())
    app.add_handler(MainMenu.get_conversation_handler())
    app.add_handler(ProfileMenu.get_conversation_handler())
    app.add_handler(SearchMenu.get_conversation_handler())
    app.add_handler(ConnectionHandlers.get_conversation_handler())
    app.add_handler(NotificationHandlers.get_handlers())

def main():
    """Точка входа в приложение"""
    app = Application.builder().token(Config.TOKEN).build()
    setup_handlers(app)
    app.run_polling()

if __name__ == "__main__":
    main()