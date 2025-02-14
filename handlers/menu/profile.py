from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from config import Config
from database.core import DatabaseManager
from utils.geocoder import Geocoder, GeocodingError
from handlers.menu.main import MainMenu
import logging

logger = logging.getLogger(__name__)

class ProfileMenu:
    @staticmethod
    async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отображение профиля пользователя"""
        user_id = update.effective_user.id
        user_data = await DatabaseManager.fetch_one(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        
        text = (
            f"👤 *Ваш профиль*\n\n"
            f"📝 Имя: {user_data['full_name']}\n"
            f"📍 Город: {user_data['city']}\n"
            f"📅 Дата регистрации: {user_data['created_at']}"
        )
        
        keyboard = [
            [InlineKeyboardButton("✏️ Изменить имя", callback_data="edit_name")],
            [InlineKeyboardButton("🌍 Изменить город", callback_data="edit_city")],
            [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")]
        ]
        
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return Config.PROFILE_EDITING

    @staticmethod
    async def handle_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка редактирования профиля"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "edit_name":
            await query.edit_message_text("Введите новое имя:")
            return Config.PROFILE_EDITING_NAME
            
        elif query.data == "edit_city":
            await query.edit_message_text("Введите новый город или отправьте геолокацию:")
            return Config.PROFILE_EDITING_CITY
            
        return await MainMenu.show_main_menu(update, context)

    @staticmethod
    async def update_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обновление имени пользователя"""
        new_name = update.message.text.strip()
        if len(new_name.split()) < 2:
            await update.message.reply_text("❌ Введите имя и фамилию через пробел")
            return Config.PROFILE_EDITING_NAME

        await DatabaseManager.execute(
            "UPDATE users SET full_name = ? WHERE user_id = ?",
            (new_name, update.effective_user.id)
        )  # Закрывающая скобка добавлена здесь
        
        await update.message.reply_text("✅ Имя успешно обновлено!")
        return await MainMenu.show_main_menu(update, context)

    @staticmethod
    async def update_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обновление города пользователя"""
        try:
            if update.message.location:
                lat = update.message.location.latitude
                lon = update.message.location.longitude
                city = await Geocoder.reverse_geocode(lat, lon)
            else:
                city = update.message.text
                lat, lon = await Geocoder.get_coordinates(city)

            await DatabaseManager.execute(
                "UPDATE users SET city = ?, lat = ?, lon = ? WHERE user_id = ?",
                (city, lat, lon, update.effective_user.id)
            )  # Закрывающая скобка добавлена здесь
            
            await update.message.reply_text("✅ Город успешно обновлен!")
            return await MainMenu.show_main_menu(update, context)
            
        except GeocodingError as e:
            await update.message.reply_text(f"❌ Ошибка определения локации: {e}")
            return Config.PROFILE_EDITING_CITY
        except Exception as e:
            logger.error(f"Ошибка обновления города: {e}")
            await update.message.reply_text("🚨 Произошла ошибка, попробуйте позже")
            return ConversationHandler.END

    @classmethod
    def get_conversation_handler(cls):
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(cls.show_profile, pattern="^menu_profile$")],
        states={
            Config.PROFILE_EDITING: [
                CallbackQueryHandler(cls.handle_profile_edit),
                MessageHandler(filters.TEXT & ~filters.COMMAND, cls.update_name)
            ],
            Config.PROFILE_EDITING_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cls.update_name)
            ],
            Config.PROFILE_EDITING_CITY: [
                MessageHandler(filters.TEXT | filters.LOCATION, cls.update_city)
            ]
        },
        fallbacks=[CommandHandler('cancel', lambda u,c: ConversationHandler.END)],
        per_message=False
        )
