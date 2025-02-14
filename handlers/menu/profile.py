from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import Config
from database.core import DatabaseManager
from utils.localization import translate

class ProfileMenu:
    @staticmethod
    async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отображение профиля"""
        user_id = update.effective_user.id
        user_data = await DatabaseManager.fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
        
        text = translate("profile_text", context.user_data.get("language", Config.DEFAULT_LANGUAGE)).format(
            name=user_data['full_name'],
            city=user_data['city'],
            skills=user_data['skills'],
            hobbies=user_data['hobbies']
        )
        
        keyboard = [
            [InlineKeyboardButton(translate("edit_profile_button", context.user_data.get("language", Config.DEFAULT_LANGUAGE)), callback_data="edit_profile")]
        ]
        
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return Config.PROFILE_EDITING