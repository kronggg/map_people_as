from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from config import Config
from utils.localization import translate
import logging

logger = logging.getLogger(__name__)

class MainMenu:
    @staticmethod
    async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            keyboard = [
                [KeyboardButton("👤 Профиль"), KeyboardButton("🔍 Поиск")],
                [KeyboardButton("⚙ Настройки")]
            ]
            
            await update.message.reply_text(
                "🏠 Главное меню",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
            )
            return Config.MAIN_MENU
        except Exception as e:
            logger.error(f"Menu error: {str(e)}")
            return ConversationHandler.END

    @classmethod
    def get_conversation_handler(cls):
        return ConversationHandler(
            entry_points=[CommandHandler('menu', cls.show_menu)],
            states={
                Config.MAIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, cls.show_menu)
                ]
            },
            fallbacks=[CommandHandler('cancel', lambda u,c: ConversationHandler.END)],
            per_message=False
        )