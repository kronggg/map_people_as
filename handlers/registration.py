from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import Config
from database.core import DatabaseManager
from utils.security import Security
from utils.geocoder import Geocoder, GeocodingError
from utils.localization import translate
import pyotp
import logging

logger = logging.getLogger(__name__)

class RegistrationHandlers:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало регистрации"""
        await update.message.reply_text(
            translate("GDPR_TEXT", context.user_data.get("language", Config.DEFAULT_LANGUAGE)),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(translate("accept_button", context.user_data.get("language", Config.DEFAULT_LANGUAGE)), callback_data="gdpr_accept")]
            ])
        )
        return Config.GDPR_CONSENT

    @staticmethod
    async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода телефона"""
        phone = update.message.text
        if not Security.validate_phone(phone):
            await update.message.reply_text(translate("invalid_phone_format", context.user_data.get("language", Config.DEFAULT_LANGUAGE)))
            return Config.PHONE_INPUT
        
        context.user_data['phone'] = phone
        await update.message.reply_text(translate("enter_otp", context.user_data.get("language", Config.DEFAULT_LANGUAGE)))
        return Config.OTP_VERIFICATION

    # Остальные методы регистрации...