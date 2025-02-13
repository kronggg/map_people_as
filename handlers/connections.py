from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from database.user_repository import UserRepository
from utils.rate_limiter import RateLimiter

class ConnectionHandlers:
    @staticmethod
    async def init_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
            if not user.username:
        await update.message.reply_text("❌ Установите username в настройках Telegram, чтобы отправлять запросы.")
        return ConversationHandler.END
        
        
        """Инициирует процесс установки связи"""
        user_id = update.effective_user.id
        
        # Проверяем лимиты запросов
        async with RateLimiter().limit(user_id, 'connection_request', 3, 3600) as allowed:
            if not allowed:
                await update.message.reply_text("🚨 Превышен лимит запросов (3/час)")
                return

        await update.message.reply_text("🔍 Введите навыки для поиска:")
        return 'WAIT_SEARCH_QUERY'

    @staticmethod
    async def handle_search_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает поисковый запрос"""
        search_term = update.message.text
        context.user_data['search_term'] = search_term
        
        # Ищем пользователей
        users = await UserRepository.search_users(search_term)
        
        # Формируем клавиатуру с результатами
        buttons = [
            [InlineKeyboardButton(f"{u.full_name} (@{u.nickname})", callback_data=f"connect_{u.user_id}")]
            for u in users[:5]  # Показываем первые 5 результатов
        ]
        
        await update.message.reply_text(
            "🔎 Результаты поиска:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return 'HANDLE_CONNECTION_CHOICE'
        
    
    @staticmethod
    async def handle_connection_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает выбор пользователя из результатов поиска"""
        query = update.callback_query
        await query.answer()
        
        target_user_id = int(query.data.split('_')[1])
        initiator_id = query.from_user.id
        
        # Проверяем существующие связи
        if await UserRepository.check_existing_connection(initiator_id, target_user_id):
            await query.edit_message_text("🚨 Связь уже установлена или запрос отправлен ранее")
            return ConversationHandler.END
            
        # Создаем запрос
        success = await ConnectionService.create_connection(
            user_from=initiator_id,
            user_to=target_user_id
        )
        
        if success:
            # Отправляем уведомление целевому пользователю
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"🔔 Пользователь @{query.from_user.username} хочет связаться с вами!",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Принять", callback_data=f"accept_{initiator_id}"),
                        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{initiator_id}")
                    ]
                ])
            )
            await query.edit_message_text("📨 Запрос отправлен!")
        else:
            await query.edit_message_text("🚨 Ошибка при отправке запроса")
            
        return ConversationHandler.END
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    @staticmethod
    async def show_connections(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отображает список активных связей с пагинацией"""
        user_id = update.effective_user.id
        page = int(context.args[0]) if context.args else 0
        per_page = 5
        
        connections = await UserRepository.get_user_connections(user_id)
        total = len(connections)
        
        # Слайсинг для пагинации
        start = page * per_page
        end = start + per_page
        page_connections = connections[start:end]
        
        if not page_connections:
            await update.message.reply_text("🤷‍♂️ У вас пока нет активных связей")
            return

        # Формируем сообщение
        message = ["🔗 Ваши активные связи:\n"]
        for i, conn in enumerate(page_connections, start + 1):
            message.append(
                f"{i}. {conn['full_name']} (@{conn['nickname']})\n"
                f"Профессия: {conn['profession']}\n"
                f"Навыки: {conn['skills'][:50]}...\n"
                f"Тип: {'исходящая' if conn['direction'] == 'outgoing' else 'входящая'}\n"
            )

        # Кнопки пагинации
        buttons = []
        if page > 0:
            buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"conn_page_{page-1}"))
        if end < total:
            buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"conn_page_{page+1}"))
        
        keyboard = [buttons] if buttons else None
        
        await update.message.reply_text(
            "\n".join(message),
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
        )
        
    @staticmethod
    async def handle_connections_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает переключение страниц"""
        query = update.callback_query
        await query.answer()
        
        page = int(query.data.split("_")[-1])
        user_id = query.from_user.id
        
        # Повторно используем логику отображения
        await query.edit_message_text(
            text=await ConnectionHandlers._generate_connections_text(user_id, page),
            reply_markup=await ConnectionHandlers._generate_pagination_buttons(user_id, page)
        )
    
    @staticmethod
    async def _generate_connections_text(user_id: int, page: int) -> str:
        """Генерирует текст сообщения с пагинацией"""
        connections = await UserRepository.get_user_connections(user_id)
        start = page * 5
        end = start + 5
        
        message = [f"Страница {page + 1}\n"]
        for i, conn in enumerate(connections[start:end], start + 1):
            message.append(
                f"{i}. {conn['full_name']} (@{conn['nickname']})\n"
                f"Навыки: {conn['skills'][:50]}..."
            )
        return "\n".join(message)
    
    @staticmethod
    async def _generate_pagination_buttons(user_id: int, page: int):
        """Генерирует кнопки пагинации"""
        connections = await UserRepository.get_user_connections(user_id)
        total_pages = (len(connections) + 4) // 5
        
        buttons = []
        if page > 0:
            buttons.append(InlineKeyboardButton("⬅️", callback_data=f"conn_page_{page-1}"))
        buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data=" "))
        if (page + 1) < total_pages:
            buttons.append(InlineKeyboardButton("➡️", callback_data=f"conn_page_{page+1}"))
        
        return InlineKeyboardMarkup([buttons])
        
        
        class ConnectionHandlers:
    @staticmethod
    async def show_connections(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /my_connections"""
        # Получаем идентификатор пользователя из объекта Update
        user_id = update.effective_user.id
        
        # Парсим номер страницы из аргументов команды (если есть)
        # Пример: /my_connections 2 → page = 2
        page = int(context.args[0]) if context.args else 0
        
        # Количество элементов на странице
        per_page = 5
        
        # Получаем ВСЕ связи пользователя из базы
        connections = await UserRepository.get_user_connections(user_id)
        
        # Рассчитываем общее количество элементов
        total = len(connections)
        
        # Вычисляем начальный и конечный индексы для текущей страницы
        start = page * per_page
        end = start + per_page
        
        # Получаем подсписок для текущей страницы
        page_connections = connections[start:end]

        # Формируем сообщение
        message_lines = ["🔗 Ваши активные связи:\n"]
        
        # Перебираем связи для текущей страницы
        for i, conn in enumerate(page_connections, start + 1):
            # Форматируем информацию о связи
            connection_info = (
                f"{i}. {conn['full_name']} (@{conn['nickname']})\n"
                f"Профессия: {conn['profession']}\n"
                f"Навыки: {conn['skills'][:50]}...\n"  # Обрезаем длинные строки
                f"Тип: {'исходящая' if conn['direction'] == 'outgoing' else 'входящая'}\n"
            )
            message_lines.append(connection_info)

        # Создаем клавиатуру для пагинации
        buttons = []
        
        # Кнопка "Назад" если не на первой странице
        if page > 0:
            buttons.append(
                InlineKeyboardButton("⬅️ Назад", callback_data=f"conn_page_{page-1}")
            )
            
        # Кнопка "Вперед" если есть следующая страница
        if end < total:
            buttons.append(
                InlineKeyboardButton("Вперед ➡️", callback_data=f"conn_page_{page+1}")
            )

        # Собираем клавиатуру только если есть кнопки
        keyboard = InlineKeyboardMarkup([buttons]) if buttons else None

        # Отправляем сообщение
        await update.message.reply_text(
            text="\n".join(message_lines),
            reply_markup=keyboard
        )
        
    @staticmethod
    async def handle_connections_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает нажатие кнопок пагинации"""
        # Получаем callback-запрос
        query = update.callback_query
        await query.answer()  # Убираем "часики" у кнопки
        
        # Извлекаем номер страницы из callback_data (conn_page_2 → 2)
        page = int(query.data.split("_")[-1])
        
        # Получаем ID пользователя
        user_id = query.from_user.id
        
        # Генерируем новый текст сообщения
        new_text = await ConnectionHandlers._generate_connections_text(user_id, page)
        
        # Генерируем новые кнопки пагинации
        new_keyboard = await ConnectionHandlers._generate_pagination_buttons(user_id, page)
        
        # Редактируем существующее сообщение
        await query.edit_message_text(
            text=new_text,
            reply_markup=new_keyboard
        )
    
    @staticmethod
    async def _generate_connections_text(user_id: int, page: int) -> str:
        """Генератор текста для сообщения со связями"""
        # Получаем связи из базы
        connections = await UserRepository.get_user_connections(user_id)
        
        # Рассчитываем диапазон для страницы
        start = page * 5
        end = start + 5
        
        # Формируем заголовок
        message_lines = [f"Страница {page + 1}\n"]
        
        # Добавляем информацию о каждой связи
        for i, conn in enumerate(connections[start:end], start + 1):
            conn_line = (
                f"{i}. {conn['full_name']} (@{conn['nickname']})\n"
                f"Навыки: {conn['skills'][:50]}..."
            )
            message_lines.append(conn_line)
            
        return "\n".join(message_lines)
    
    @staticmethod
    async def _generate_pagination_buttons(user_id: int, page: int):
        """Генератор кнопок пагинации"""
        connections = await UserRepository.get_user_connections(user_id)
        
        # Рассчитываем общее количество страниц
        total_pages = (len(connections) + 4) // 5  # Округление вверх
        
        buttons = []
        # Кнопка "Назад"
        if page > 0:
            buttons.append(
                InlineKeyboardButton("⬅️", callback_data=f"conn_page_{page-1}")
            )
            
        # Индикатор текущей страницы (не кликабельный)
        buttons.append(
            InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data=" ")
        )
        
        # Кнопка "Вперед"
        if (page + 1) < total_pages:
            buttons.append(
                InlineKeyboardButton("➡️", callback_data=f"conn_page_{page+1}")
            )
            
        return InlineKeyboardMarkup([buttons])
        
    async def handle_connection_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    target_user_id = int(query.data.split('_')[1])
    initiator_id = update.effective_user.id

    # Получаем username обоих пользователей
    initiator = await UserRepository.get_user(initiator_id)
    target_user = await UserRepository.get_user(target_user_id)

    if not initiator.username or not target_user.username:
        await query.edit_message_text("⚠️ Для связи оба пользователя должны иметь username.")
        return

    # Обновляем статус связи
    await ConnectionService.update_connection_status(target_user_id, initiator_id, "accepted")

    # Отправляем username друг другу
    await context.bot.send_message(
        chat_id=initiator_id,
        text=f"✅ {target_user.full_name} (@{target_user.username}) принял ваш запрос!"
    )

    await context.bot.send_message(
        chat_id=target_user_id,
        text=f"✅ Вы поделились своим username с {initiator.full_name} (@{initiator.username})!"
    )
