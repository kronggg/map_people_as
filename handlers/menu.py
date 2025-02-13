def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Мои связи", callback_data="my_connections")],
        # ... остальные кнопки ...
    ])
    
    