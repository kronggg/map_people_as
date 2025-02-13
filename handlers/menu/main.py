from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import Config
from database.core import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class MainMenu:
    @staticmethod
    async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отображение главного меню"""
        try:
            keyboard = [
                [InlineKeyboardButton("👤 Мой профиль", callback_data="menu_profile")],
                [InlineKeyboardButton("🔍 Поиск связей", callback_data="menu_search")],
                [InlineKeyboardButton("📨 Мои подключения", callback_data="menu_connections")],
                [InlineKeyboardButton("⚙️ Настройки", callback_data="menu_settings")]
            ]
            
            await update.callback_query.edit_message_text(
                Config.MENU_TEXTS['main'],
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return Config.MAIN_MENU
            
        except Exception as e:
            logger.error(f"Ошибка отображения меню: {e}")
            return ConversationHandler.END

    @staticmethod
    async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка навигации по меню"""
        query = update.callback_query
        await query.answer()
        
        handlers = {
            'menu_profile': ProfileMenu.show_profile,
            'menu_search': SearchMenu.show_search,
            'menu_connections': ConnectionsMenu.show_connections,
            'menu_settings': SettingsMenu.show_settings
        }
        
        return await handlers[query.data](update, context)

    @classmethod
    def get_handlers(cls):
        return [
            CallbackQueryHandler(cls.handle_navigation, pattern="^menu_")
        ]