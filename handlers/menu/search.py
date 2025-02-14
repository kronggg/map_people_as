from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)
from config import Config
from database.core import DatabaseManager
from utils.rate_limiter import RateLimiter
from utils.geocoder import Geocoder, GeocodingError
from handlers.menu.main import MainMenu
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SearchMenu:
    _RESULTS_PER_PAGE = 5

    @staticmethod
    async def show_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Инициализация поиска с выбором фильтров"""
        try:
            keyboard = [
                [InlineKeyboardButton("📍 По местоположению", callback_data="search_location")],
                [InlineKeyboardButton("🔍 По навыкам", callback_data="search_skills")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            
            await update.callback_query.edit_message_text(
                "🔍 *Выберите тип поиска:*",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return Config.SEARCH_FILTERS
            
        except Exception as e:
            logger.error(f"Search init error: {e}")
            await update.callback_query.edit_message_text("❌ Ошибка инициализации поиска")
            return ConversationHandler.END

    @staticmethod
    async def handle_location_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка поиска по местоположению"""
        query = update.callback_query
        await query.answer()
        
        context.user_data['search_type'] = 'location'
        await query.edit_message_text("🌍 Введите город или отправьте геолокацию:")
        return Config.SEARCH_LOCATION_INPUT

    @staticmethod
    async def handle_skills_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка поиска по навыкам"""
        query = update.callback_query
        await query.answer()
        
        context.user_data['search_type'] = 'skills'
        await query.edit_message_text("📝 Введите навыки через запятую:")
        return Config.SEARCH_SKILLS_INPUT

    @staticmethod
    async def process_search_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка введенных пользователем данных для поиска"""
        user_id = update.effective_user.id
        search_type = context.user_data.get('search_type')
        
        try:
            # Проверка лимита запросов
            if not RateLimiter().check(user_id, 'search'):
                await update.message.reply_text("🚨 Превышен лимит поисковых запросов")
                return await MainMenu.show_main_menu(update, context)

            # Обработка ввода данных
            if search_type == 'location':
                if update.message.location:
                    lat = update.message.location.latitude
                    lon = update.message.location.longitude
                    city = await Geocoder.reverse_geocode(lat, lon)
                else:
                    city = update.message.text
                    coordinates = await Geocoder.get_coordinates(city)
                    lat, lon = coordinates
                
                context.user_data['search_params'] = {
                    'lat': lat,
                    'lon': lon,
                    'radius': 50  # Радиус в км
                }
                
            elif search_type == 'skills':
                skills = [skill.strip().lower() for skill in update.message.text.split(',')]
                context.user_data['search_params'] = {
                    'skills': skills
                }

            # Выполнение поиска
            results = await SearchMenu._perform_search(context.user_data)
            
            if not results:
                await update.message.reply_text("😞 Ничего не найдено")
                return await MainMenu.show_main_menu(update, context)

            context.user_data['search_results'] = results
            context.user_data['current_page'] = 0
            
            return await SearchMenu._display_results_page(update, context)

        except GeocodingError as e:
            await update.message.reply_text(f"❌ Ошибка геокодирования: {e}")
            return Config.SEARCH_FILTERS
        except Exception as e:
            logger.error(f"Search error: {e}")
            await update.message.reply_text("🚨 Произошла ошибка при поиске")
            return ConversationHandler.END

    @staticmethod
    async def _perform_search(params: Dict[str, Any]) -> list:
        """Выполнение поиска в базе данных"""
        search_type = params.get('search_type')
        
        if search_type == 'location':
            query = """
                SELECT user_id, full_name, city, lat, lon 
                FROM users 
                WHERE (
                    6371 * acos(
                        cos(radians(:lat)) * cos(radians(lat)) * 
                        cos(radians(lon) - radians(:lon)) + 
                        sin(radians(:lat)) * sin(radians(lat))
                    ) <= :radius
                ORDER BY created_at DESC
                LIMIT 50
            """
            return await DatabaseManager.fetch(query, params['search_params'])
        
        elif search_type == 'skills':
            skills = params['search_params']['skills']
            query = """
                SELECT user_id, full_name, skills 
                FROM users 
                WHERE LOWER(skills) LIKE ?
                ORDER BY created_at DESC
                LIMIT 50
            """
            return await DatabaseManager.fetch(query, (f"%{skills[0]}%",))
        
        return []

    @staticmethod
    async def _display_results_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отображение страницы с результатами поиска"""
        current_page = context.user_data['current_page']
        results = context.user_data['search_results']
        total_pages = (len(results) + SearchMenu._RESULTS_PER_PAGE - 1) // SearchMenu._RESULTS_PER_PAGE
        
        start_idx = current_page * SearchMenu._RESULTS_PER_PAGE
        end_idx = start_idx + SearchMenu._RESULTS_PER_PAGE
        page_results = results[start_idx:end_idx]

        # Формирование сообщения
        message_text = "🔍 *Результаты поиска:*\n\n"
        for idx, user in enumerate(page_results, start=1):
            message_text += f"{idx}. {user['full_name']}"
            if 'city' in user:
                message_text += f" ({user['city']})"
            message_text += "\n"

        # Формирование клавиатуры
        keyboard = []
        for user in page_results:
            keyboard.append([
                InlineKeyboardButton(
                    user['full_name'],
                    callback_data=f"view_profile_{user['user_id']}"
                )
            ])

        # Добавление пагинации
        pagination = []
        if current_page > 0:
            pagination.append(InlineKeyboardButton("◀️ Назад", callback_data="prev_page"))
        if end_idx < len(results):
            pagination.append(InlineKeyboardButton("Вперед ▶️", callback_data="next_page"))
        
        if pagination:
            keyboard.append(pagination)

        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])

        await update.message.reply_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return Config.SEARCH_RESULTS

    @staticmethod
    async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка переключения страниц"""
        query = update.callback_query
        await query.answer()
        
        action = query.data
        current_page = context.user_data['current_page']
        
        if action == 'prev_page':
            context.user_data['current_page'] = max(0, current_page - 1)
        elif action == 'next_page':
            context.user_data['current_page'] += 1
            
        await query.delete_message()
        return await SearchMenu._display_results_page(update, context)

    @staticmethod
    async def view_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр профиля пользователя из результатов поиска"""
        query = update.callback_query
        await query.answer()
        
        user_id = int(query.data.split('_')[-1])
        user_data = await DatabaseManager.fetch_one(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        
        text = (
            f"👤 *Профиль пользователя*\n\n"
            f"📝 Имя: {user_data['full_name']}\n"
            f"📍 Город: {user_data.get('city', 'не указан')}\n"
            f"🛠 Навыки: {user_data.get('skills', 'не указаны')}"
        )
        
        keyboard = [
            [InlineKeyboardButton("📨 Отправить запрос", callback_data=f"connect_{user_id}")],
            [InlineKeyboardButton("🔙 Назад к результатам", callback_data="back_to_results")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return Config.VIEW_PROFILE

    @classmethod
    def get_conversation_handler(cls):
        """Фабрика для регистрации обработчика"""
        return ConversationHandler(
            entry_points=[CallbackQueryHandler(cls.show_search, pattern="^menu_search$")],
            states={
                Config.SEARCH_FILTERS: [
                    CallbackQueryHandler(cls.handle_location_search, pattern="^search_location$"),
                    CallbackQueryHandler(cls.handle_skills_search, pattern="^search_skills$"),
                    CallbackQueryHandler(MainMenu.show_main_menu, pattern="^main_menu$")
                ],
                Config.SEARCH_LOCATION_INPUT: [
                    MessageHandler(filters.TEXT | filters.LOCATION, cls.process_search_input)
                ],
                Config.SEARCH_SKILLS_INPUT: [
                    MessageHandler(filters.TEXT, cls.process_search_input)
                ],
                Config.SEARCH_RESULTS: [
                    CallbackQueryHandler(cls.handle_pagination, pattern="^(prev_page|next_page)$"),
                    CallbackQueryHandler(cls.view_profile, pattern="^view_profile_"),
                    CallbackQueryHandler(MainMenu.show_main_menu, pattern="^main_menu$")
                ],
                Config.VIEW_PROFILE: [
                    CallbackQueryHandler(cls._display_results_page, pattern="^back_to_results$"),
                    CallbackQueryHandler(MainMenu.show_main_menu, pattern="^main_menu$")
                ]
            },
            fallbacks=[CommandHandler('cancel', lambda u,c: ConversationHandler.END)],
            allow_reentry=True
        )
