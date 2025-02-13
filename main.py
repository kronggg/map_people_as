##############################################
# main.py - Главный модуль запуска бота
##############################################

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from config import Config
from handlers.registration import RegistrationHandlers
from handlers.connections import ConnectionHandlers
from handlers.notifications import NotificationHandlers
from database.core import Database

def setup_handlers(application):
    """Регистрация всех обработчиков"""
    
    # Обработчик регистрации
    reg_conv = ConversationHandler(
        entry_points=[CommandHandler('start', RegistrationHandlers.start)],
        states={
            Config.GDPR_CONSENT: [
                CallbackQueryHandler(RegistrationHandlers.handle_gdpr_choice)
            ],
            Config.ENTER_PHONE: [
                MessageHandler(filters.TEXT, RegistrationHandlers.enter_phone)
            ],
            Config.VERIFY_OTP: [
                MessageHandler(filters.TEXT, RegistrationHandlers.verify_otp)
            ]
        },
        fallbacks=[CommandHandler('cancel', RegistrationHandlers.cancel)]
    )
    
    # Обработчик связей
    connection_conv = ConversationHandler(
        entry_points=[CommandHandler('connect', ConnectionHandlers.init_connection)],
        states={
            'WAIT_SEARCH_QUERY': [
                MessageHandler(filters.TEXT, ConnectionHandlers.handle_search_query)
            ],
            'HANDLE_CONNECTION_CHOICE': [
                CallbackQueryHandler(ConnectionHandlers.handle_connection_choice)
            ]
        },
        fallbacks=[CommandHandler('cancel', ConnectionHandlers.cancel)]
    )

    # Регистрация всех обработчиков
    application.add_handlers([
        reg_conv,
        connection_conv,
        CommandHandler('my_connections', ConnectionHandlers.show_connections),
        CallbackQueryHandler(
            NotificationHandlers.handle_connection_response,
            pattern=r"^(accept|reject)_\d+$"
        ),
        CallbackQueryHandler(
            ConnectionHandlers.handle_connections_pagination,
            pattern=r"^conn_page_\d+$"
        )
    ])

def main():
    # Инициализация приложения
    application = Application.builder().token(Config.TOKEN).build()
    
    # Инициализация БД
    application.add_handler(CommandHandler('init_db', Database.init_db))
    
    # Настройка обработчиков
    setup_handlers(application)
    
    # Запуск бота (всегда последний!)
    application.run_polling()

if __name__ == "__main__":
    main()
