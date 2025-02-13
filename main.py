##############################################
# main.py - Инициализация и запуск бота
##############################################

from config import Config
from handlers import RegistrationHandlers
from database import Database

def main():
    # Инициализация приложения
    application = Application.builder().token(Config.TOKEN).build()
    
    # Инициализация БД
    application.add_handler(CommandHandler('init_db', Database.init_db))
    
    # Регистрация обработчиков
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', RegistrationHandlers.start)],
        states={
            # ... остальные состояния
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler)
    
    # Запуск бота
    application.run_polling()
    
    # Добавляем импорт
from handlers.connections import ConnectionHandlers

    # Регистрируем обработчик связей
    connection_conv = ConversationHandler(
        entry_points=[CommandHandler('connect', ConnectionHandlers.init_connection)],
        states={
            'WAIT_SEARCH_QUERY': [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ConnectionHandlers.handle_search_query)
            ],
            'HANDLE_CONNECTION_CHOICE': [
                CallbackQueryHandler(ConnectionHandlers.handle_connection_choice)
            ]
        },
        fallbacks=[CommandHandler('cancel', ConnectionHandlers.cancel)]
    )
    application.add_handler(connection_conv)
    
    # Добавляем новый импорт
from handlers.notifications import NotificationHandlers

    # Регистрируем обработчик ответов
    application.add_handler(CallbackQueryHandler(
        NotificationHandlers.handle_connection_response,
        pattern=r"^(accept|reject)_\d+$"
    ))
    
    # Регистрация команды /my_connections
    application.add_handler(CommandHandler(
        "my_connections", 
        ConnectionHandlers.show_connections
    ))
    
    # Регистрация обработчика пагинации
    application.add_handler(CallbackQueryHandler(
        ConnectionHandlers.handle_connections_pagination,
        pattern=r"^conn_page_\d+$"
    ))

if __name__ == "__main__":
    main()