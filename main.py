import logging
from telegram.ext import Application, CommandHandler, ConversationHandler
from config import Config
from database.core import DatabaseManager
from handlers.registration import RegistrationHandlers
from handlers.menu.main import MainMenu
from handlers.menu.profile import ProfileMenu
from handlers.menu.search import SearchMenu
from handlers.connections import ConnectionHandlers
from handlers.notifications import NotificationHandlers
from utils.rate_limiter import RateLimiter
from utils.security import Security
from utils.geocoder import Geocoder

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def init_database():
    """Инициализация базы данных"""
    try:
        await DatabaseManager.execute(
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                phone_hash TEXT UNIQUE,
                full_name TEXT NOT NULL,
                city TEXT,
                lat REAL,
                lon REAL,
                skills TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        
        await DatabaseManager.execute(
            """CREATE TABLE IF NOT EXISTS connections (
                connection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_from INTEGER NOT NULL,
                user_to INTEGER NOT NULL,
                status TEXT CHECK(status IN ('pending', 'accepted', 'rejected')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_from) REFERENCES users(user_id),
                FOREIGN KEY(user_to) REFERENCES users(user_id)
            )"""
        )
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def setup_handlers(app: Application) -> None:
    """Регистрация всех обработчиков"""
    
    # Регистрация пользователя
    registration_handler = RegistrationHandlers.get_conversation_handler()
    
    # Главное меню
    menu_handlers = [
        CommandHandler('menu', MainMenu.show_main_menu),
        *MainMenu.get_handlers()
    ]
    
    # Профиль пользователя
    profile_handler = ProfileMenu.get_conversation_handler()
    
    # Система поиска
    search_handler = SearchMenu.get_conversation_handler()
    
    # Управление подключениями
    connection_handlers = [
        ConnectionHandlers.get_conversation_handler(),
        *ConnectionHandlers.get_callbacks()
    ]
    
    # Уведомления
    notification_handlers = NotificationHandlers.get_handlers()
    
    # Регистрация всех обработчиков
    handlers = [
        registration_handler,
        *menu_handlers,
        profile_handler,
        search_handler,
        *connection_handlers,
        *notification_handlers
    ]
    
    for handler in handlers:
        app.add_handler(handler)

    # Общие команды
    app.add_handler(CommandHandler('start', RegistrationHandlers.start))
    app.add_handler(CommandHandler('help', help_command))

async def help_command(update, context):
    """Обработчик команды /help"""
    help_text = (
        "📚 Доступные команды:\n"
        "/start - Начать регистрацию\n"
        "/menu - Главное меню\n"
        "/help - Справка\n"
        "/connect - Найти связи\n"
    )
    await update.message.reply_text(help_text)

async def post_init(app: Application) -> None:
    """Действия после инициализации"""
    await init_database()
    await Geocoder.warmup()  # Предварительная инициализация геокодера
    RateLimiter()  # Проверка подключения к Redis
    logger.info("Application initialization complete")

def main() -> None:
    """Точка входа в приложение"""
    app = Application.builder() \
        .token(Config.TOKEN) \
        .post_init(post_init) \
        .build()

    setup_handlers(app)
    
    # Настройка middleware
    app.add_handler(MessageHandler(filters.ALL, Security.message_filter))
    
    logger.info("Starting bot in polling mode...")
    app.run_polling(
        poll_interval=1.0,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()