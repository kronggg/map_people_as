import logging
from telegram.ext import Application
from config import Config
from handlers.registration import RegistrationHandlers
from handlers.menu.main import MainMenu
from handlers.menu.profile import ProfileMenu
from handlers.menu.search import SearchMenu
from database.core import DatabaseManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def init_database():
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
    app.add_handler(RegistrationHandlers.get_conversation_handler())
    app.add_handler(MainMenu.get_conversation_handler())
    app.add_handler(ProfileMenu.get_conversation_handler())
    app.add_handler(SearchMenu.get_conversation_handler())
    # Удалён ошибочный вызов ConnectionHandlers

def main():
    app = Application.builder().token(Config.TOKEN).build()
    setup_handlers(app)
    app.run_polling()

if __name__ == "__main__":
    main()