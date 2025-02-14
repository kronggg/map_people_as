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
    await DatabaseManager.execute('''CREATE TABLE IF NOT EXISTS users (...)''')

def setup_handlers(app):
    app.add_handler(RegistrationHandlers.get_conversation_handler())
    app.add_handler(MainMenu.get_conversation_handler())

def main():
    app = Application.builder().token(Config.TOKEN).build()
    app.run_polling()

if __name__ == "__main__":
    main()