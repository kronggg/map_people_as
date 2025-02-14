from telegram import (
    Update, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    LabeledPrice, 
    ShippingOption
)
from telegram.ext import (
    ConversationHandler,
    ContextTypes, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters
)
from config import Config
from database.core import DatabaseManager
from utils.rate_limiter import RateLimiter
from utils.security import Security
import logging
import re

logger = logging.getLogger(__name__)

class ConnectionHandlers:
    """Обработчики системы установки связей между пользователями"""

    @staticmethod
    async def init_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Инициирует процесс установки связи"""
        user_id = update.effective_user.id
        
        # Проверка лимита запросов
        if not RateLimiter().check(user_id, 'connection'):
            await update.message.reply_text("🚨 Превышен лимит запросов (3/час)")
            return

        await update.message.reply_text("🔍 Введите навыки для поиска (через запятую):")
        return Config.SEARCH_QUERY

    @staticmethod
    async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка поискового запроса"""
        search_terms = [term.strip().lower() for term in update.message.text.split(',')]
        context.user_data['search_terms'] = search_terms

        try:
            # Поиск пользователей по навыкам
            results = await DatabaseManager.fetch(
                """SELECT user_id, full_name, skills 
                FROM users 
                WHERE LOWER(skills) LIKE ? 
                LIMIT ?""",
                (f"%{search_terms[0]}%", Config.SEARCH_RESULTS_LIMIT)
            )

            if not results:
                await update.message.reply_text("😞 Никого не найдено")
                return ConversationHandler.END

            # Формируем клавиатуру с результатами
            keyboard = [
                [InlineKeyboardButton(
                    f"{row[1]} ({row[2][:15]}...)",
                    callback_data=f"conn_select_{row[0]}"
                )] for row in results
            ]

            await update.message.reply_text(
                "🔎 Результаты поиска:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return Config.CONNECTION_SELECT

        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            await update.message.reply_text("⚠️ Произошла ошибка при поиске")
            return ConversationHandler.END

    @staticmethod
    async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора пользователя"""
        query = update.callback_query
        await query.answer()
        
        target_user_id = int(query.data.split('_')[-1])
        initiator_id = query.from_user.id

        # Проверка существующей связи
        existing = await DatabaseManager.fetch_one(
            """SELECT 1 FROM connections 
            WHERE (user_from = ? AND user_to = ?)
            OR (user_from = ? AND user_to = ?)""",
            (initiator_id, target_user_id, target_user_id, initiator_id)
        )

        if existing:
            await query.edit_message_text("⚠️ Связь уже установлена ранее")
            return ConversationHandler.END

        # Сохранение запроса
        await DatabaseManager.execute(
            """INSERT INTO connections 
            (user_from, user_to, status) 
            VALUES (?, ?, 'pending')""",
            (initiator_id, target_user_id)
        )

        # Отправка уведомления целевому пользователю
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"🔔 Новый запрос на связь от @{query.from_user.username}!\n"
                     f"Навыки: {', '.join(context.user_data['search_terms'])}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Принять", callback_data=f"conn_accept_{initiator_id}"),
                     InlineKeyboardButton("❌ Отклонить", callback_data=f"conn_reject_{initiator_id}")]
                ])
            )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")

        await query.edit_message_text("📨 Запрос отправлен!")
        return ConversationHandler.END

    @staticmethod
    async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ответа на запрос связи"""
        query = update.callback_query
        await query.answer()
        
        action, initiator_id = query.data.split('_')[1:]
        target_user_id = query.from_user.id

        # Обновление статуса связи
        new_status = 'accepted' if action == 'accept' else 'rejected'
        await DatabaseManager.execute(
            """UPDATE connections 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE user_from = ? AND user_to = ?""",
            (new_status, initiator_id, target_user_id)
        )

        # Уведомление инициатора
        try:
            status_text = "принял" if new_status == 'accepted' else "отклонил"
            await context.bot.send_message(
                chat_id=initiator_id,
                text=f"Пользователь @{query.from_user.username} {status_text} ваш запрос!"
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления: {e}")

        await query.edit_message_text(f"✅ Статус обновлен: {new_status}")
        return ConversationHandler.END

    @staticmethod
    def get_conversation_handler(cls):
        return ConversationHandler(
        entry_points=[CommandHandler('connect', cls.init_connection)],
        states={
            Config.SEARCH_QUERY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, cls.handle_search)
            ],
            Config.CONNECTION_SELECT: [
                CallbackQueryHandler(cls.handle_selection, pattern=r"^conn_select_\d+$")
            ]
        },
        fallbacks=[CommandHandler('cancel', lambda u,c: ConversationHandler.END)],
        per_message=False
    )

    @staticmethod
    def get_callbacks():
        """Регистрация callback-обработчиков"""
        return [
            CallbackQueryHandler(
                ConnectionHandlers.handle_response, 
                pattern=r"^conn_(accept|reject)_\d+$"
            )
        ]
