from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters
from config import Config
from database.core import DatabaseManager
from utils.geocoder import Geocoder

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