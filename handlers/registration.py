from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
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
        try:
            keyboard = [[KeyboardButton(translate("accept_button", Config.DEFAULT_LANGUAGE))]]
            await update.message.reply_text(
                translate("GDPR_TEXT", Config.DEFAULT_LANGUAGE),
                reply_markup=ReplyKeyboardMarkup(
                    keyboard, 
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
            )
            return Config.GDPR_CONSENT
        except Exception as e:
            logger.error(f"Start error: {str(e)}")
            return ConversationHandler.END

    @staticmethod
    async def handle_gdpr_accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            expected_text = translate("accept_button", Config.DEFAULT_LANGUAGE)
            if update.message.text != expected_text:
                await update.message.reply_text(translate("gdpr_error", Config.DEFAULT_LANGUAGE))
                return Config.GDPR_CONSENT
                
            await update.message.reply_text(
                translate("enter_phone", Config.DEFAULT_LANGUAGE),
                reply_markup=ReplyKeyboardMarkup.remove_keyboard()
            )
            return Config.PHONE_INPUT
        except Exception as e:
            logger.error(f"GDPR accept error: {str(e)}")
            return ConversationHandler.END

    @staticmethod
    async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            phone = update.message.text
            if not Security.validate_phone(phone):
                await update.message.reply_text(translate("invalid_phone_format", Config.DEFAULT_LANGUAGE))
                return Config.PHONE_INPUT
            
            context.user_data['phone'] = phone
            context.user_data['otp_secret'] = pyotp.random_base32()
            otp_code = pyotp.TOTP(context.user_data['otp_secret']).now()
            
            await update.message.reply_text(
                translate("enter_otp", Config.DEFAULT_LANGUAGE).format(otp_code=otp_code)
            )
            return Config.OTP_VERIFICATION
        except Exception as e:
            logger.error(f"Phone handling error: {str(e)}")
            return ConversationHandler.END

    @staticmethod
    async def verify_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_code = update.message.text.strip()
            stored_secret = context.user_data.get('otp_secret')
            
            if not pyotp.TOTP(stored_secret).verify(user_code):
                await update.message.reply_text(translate("invalid_otp", Config.DEFAULT_LANGUAGE))
                return Config.OTP_VERIFICATION

            await update.message.reply_text(translate("enter_full_name", Config.DEFAULT_LANGUAGE))
            return Config.FULL_NAME
        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            return ConversationHandler.END

    @staticmethod
    async def handle_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            full_name = update.message.text.strip()
            if len(full_name.split()) < 2:
                await update.message.reply_text(translate("invalid_full_name", Config.DEFAULT_LANGUAGE))
                return Config.FULL_NAME

            context.user_data['full_name'] = full_name
            await update.message.reply_text(translate("enter_city", Config.DEFAULT_LANGUAGE))
            return Config.CITY
        except Exception as e:
            logger.error(f"Full name error: {str(e)}")
            return ConversationHandler.END

    @staticmethod
    async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if update.message.location:
                lat = update.message.location.latitude
                lon = update.message.location.longitude
                city = await Geocoder.reverse_geocode(lat, lon)
            else:
                city = update.message.text
                lat, lon = await Geocoder.get_coordinates(city)

            await DatabaseManager.execute(
                '''INSERT INTO users 
                (user_id, phone_hash, full_name, city, lat, lon, language)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (
                    update.effective_user.id,
                    Security.get_hash(context.user_data['phone']),
                    context.user_data['full_name'],
                    city,
                    lat,
                    lon,
                    Config.DEFAULT_LANGUAGE
                )
            )

            await update.message.reply_text(
                translate("registration_complete", Config.DEFAULT_LANGUAGE),
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("/menu")]],
                    resize_keyboard=True
                )
            )
            return ConversationHandler.END
        except GeocodingError as e:
            await update.message.reply_text(translate("geocoding_error", Config.DEFAULT_LANGUAGE).format(error=str(e)))
            return Config.CITY
        except Exception as e:
            logger.error(f"Registration final error: {str(e)}")
            await update.message.reply_text(translate("registration_error", Config.DEFAULT_LANGUAGE))
            return ConversationHandler.END

    @staticmethod
    def get_conversation_handler():
        return ConversationHandler(
            entry_points=[CommandHandler('start', RegistrationHandlers.start)],
            states={
                Config.GDPR_CONSENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, RegistrationHandlers.handle_gdpr_accept)
                ],
                Config.PHONE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, RegistrationHandlers.handle_phone)],
                Config.OTP_VERIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, RegistrationHandlers.verify_otp)],
                Config.FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, RegistrationHandlers.handle_full_name)],
                Config.CITY: [MessageHandler(filters.TEXT | filters.LOCATION, RegistrationHandlers.handle_city)]
            },
            fallbacks=[CommandHandler('cancel', lambda u,c: ConversationHandler.END)],
            per_message=False
        )