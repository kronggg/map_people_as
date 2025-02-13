from utils.security import Security

class RegistrationHandlers:
    @staticmethod
    async def verify_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Верификация OTP и переход к сбору ФИО"""
        user_code = update.message.text
        stored_secret = context.user_data.get('otp_secret')
        
        if not Security.verify_otp(stored_secret, user_code):
            await update.message.reply_text("❌ Неверный код. Попробуйте ещё раз.")
            return Config.VERIFY_OTP
        
        # Очистка временных данных
        del context.user_data['otp_secret']
        
        await update.message.reply_text("✅ Телефон подтверждён! Введите ваше полное имя:")
        return Config.ENTER_FULL_NAME
        
class RegistrationHandlers:
    @staticmethod
    async def enter_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода ФИО с валидацией"""
        full_name = update.message.text.strip()
        
        if len(full_name.split()) < 2:
            await update.message.reply_text("❌ Введите имя и фамилию через пробел")
            return Config.ENTER_FULL_NAME
            
        context.user_data['full_name'] = full_name
        await update.message.reply_text("🌍 Введите ваш город:")
        return Config.ENTER_CITY
        
from utils.geocoder import Geocoder

class RegistrationHandlers:
    @staticmethod
    async def enter_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода города и определение координат"""
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
        
        await self._save_user_data(context)
        await self._show_main_menu(update)
        return ConversationHandler.END
        
class RegistrationHandlers:
    async def _save_user_data(self, context: ContextTypes.DEFAULT_TYPE):
        """Сохранение данных пользователя в БД"""
        user_data = context.user_data
        phone_hash = Security.get_hash(user_data['phone'])
        
        async with Database() as db:
            await db.execute('''
                INSERT INTO users 
                (user_id, phone_hash, full_name, city, lat, lon)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                context.user.id,
                phone_hash,
                user_data['full_name'],
                user_data['city'],
                user_data['latitude'],
                user_data['longitude']
            ))
            await db.commit()
            
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils.validators import validate_geo, normalize_skills

class RegistrationHandlers:
    async def _handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка геолокации с расширенной валидацией"""
        location = update.message.location
        user_data = context.user_data
        
        try:
            # Валидация координат
            if not validate_geo(location.latitude, location.longitude):
                raise ValidationError("Invalid coordinates")
            
            # Определение страны по координатам
            country_code = await Geocoder.get_country_code(
                location.latitude, 
                location.longitude
            )
            
            user_data.update({
                'latitude': location.latitude,
                'longitude': location.longitude,
                'country_code': country_code
            })
            
            # Переход к сбору профессиональных данных
            keyboard = [
                [InlineKeyboardButton("Пропустить", callback_data="skip_profession")]
            ]
            
            await update.message.reply_text(
                "💼 Введите вашу профессию:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return Config.ENTER_PROFESSION
        
        except GeocodingError as e:
            await update.message.reply_text(f"🚨 Ошибка определения локации: {str(e)}")
            return Config.ENTER_LOCATION

    async def _handle_skills(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка навыков с нормализацией"""
        raw_skills = update.message.text
        normalized = normalize_skills(raw_skills)
        
        if len(normalized) > 10:
            await update.message.reply_text("⚠️ Максимум 10 навыков. Уточните список:")
            return Config.ENTER_SKILLS
            
        context.user_data['skills'] = normalized
        
        # Переход к следующему этапу
        await self._show_preview(update, context)
        return Config.CONFIRM_DATA
        
        async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username  # Получаем username из Telegram-профиля

    if not username:
        await update.message.reply_text("❌ Для использования бота необходимо установить username в настройках Telegram.")
        return ConversationHandler.END

    # Сохраняем в базу
    await UserRepository.save_user(
        user_id=user.id,
        username=username,
        full_name=user.full_name,
        ...
    )