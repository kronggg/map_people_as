from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from utils.security import Security
from utils.geocoder import Geocoder, GeocodingError
from utils.validators import validate_geo, normalize_skills, ValidationError
from database.core import DatabaseManager
from config import Config

class RegistrationHandlers:
    @staticmethod
    async def verify_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Верификация OTP и переход к сбору ФИО"""
        user_code = update.message.text
        stored_secret = context.user_data.get('otp_secret')
        
        if not Security.verify_otp(stored_secret, user_code):
            await update.message.reply_text("❌ Неверный код. Попробуйте ещё раз.")
            return Config.VERIFY_OTP
        
        del context.user_data['otp_secret']
        await update.message.reply_text("✅ Телефон подтверждён! Введите ваше полное имя:")
        return Config.ENTER_FULL_NAME

    @staticmethod
    async def enter_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода ФИО"""
        full_name = update.message.text.strip()
        if len(full_name.split()) < 2:
            await update.message.reply_text("❌ Введите имя и фамилию через пробел")
            return Config.ENTER_FULL_NAME
        context.user_data['full_name'] = full_name
        await update.message.reply_text("🌍 Введите ваш город:")
        return Config.ENTER_CITY

    @staticmethod
    async def enter_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода города"""
        city = update.message.text
        try:
            lat, lon = await Geocoder.get_coordinates(city)
        except GeocodingError as e:
            await update.message.reply_text(f"❌ Ошибка определения локации: {e}")
            return Config.ENTER_CITY
        
        context.user_data.update({
            'city': city,
            'latitude': lat,
            'longitude': lon
        })
        
        await RegistrationHandlers._save_user_data(context)
        await RegistrationHandlers._show_main_menu(update)
        return ConversationHandler.END

    @staticmethod
    async def _save_user_data(context: ContextTypes.DEFAULT_TYPE):
        """Сохранение данных пользователя"""
        user_data = context.user_data
        phone_hash = Security.get_hash(user_data['phone'])
        
        await DatabaseManager.execute_query(
            '''
            INSERT INTO users 
            (user_id, phone_hash, full_name, city, lat, lon)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                context.user.id,
                phone_hash,
                user_data['full_name'],
                user_data['city'],
                user_data['latitude'],
                user_data['longitude']
            )
        )

    @staticmethod
    async def _show_main_menu(update: Update):
        """Отображение главного меню"""
        await update.message.reply_text(
            "🏠 Главное меню:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
                [InlineKeyboardButton("🔍 Поиск связей", callback_data="search")]
            )
        )

    @staticmethod
    async def _handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка геолокации"""
        location = update.message.location
        user_data = context.user_data
        
        try:
            if not validate_geo(location.latitude, location.longitude):
                raise ValidationError("Некорректные координаты")
            
            country_code = await Geocoder.get_country_code(
                location.latitude, 
                location.longitude
            )
            
            user_data.update({
                'latitude': location.latitude,
                'longitude': location.longitude,
                'country_code': country_code
            })
            
            keyboard = [[InlineKeyboardButton("Пропустить", callback_data="skip_profession")]]
            await update.message.reply_text(
                "💼 Введите вашу профессию:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            return Config.ENTER_PROFESSION
        
        except GeocodingError as e:
            await update.message.reply_text(f"🚨 Ошибка: {str(e)}")
            return Config.ENTER_LOCATION

    @staticmethod
    async def _handle_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка навыков"""
        raw_skills = update.message.text
        normalized = normalize_skills(raw_skills)
        
        if len(normalized) > 10:
            await update.message.reply_text("⚠️ Максимум 10 навыков. Уточните список:")
            return Config.ENTER_SKILLS
            
        context.user_data['skills'] = normalized
        await RegistrationHandlers._show_preview(update, context)
        return Config.CONFIRM_DATA

    @staticmethod
    async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Финализация регистрации"""
        user = update.effective_user
        
        if not user.username:
            await update.message.reply_text("❌ Установите username в настройках Telegram.")
            return ConversationHandler.END
        
        await DatabaseManager.execute_query(
            '''
            INSERT INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
            ''',
            (user.id, user.username, user.full_name)
        
        await update.message.reply_text("✅ Регистрация успешно завершена!")
        return ConversationHandler.END
