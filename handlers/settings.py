def get_privacy_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 Скрыть username", callback_data="hide_username")],
        [InlineKeyboardButton("🌐 Показывать всем", callback_data="show_username")]
    ])

async def toggle_privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action = query.data
    
    await UserRepository.update_privacy(
        user_id=query.from_user.id,
        show_username=(action == "show_username")
    )
    
    await query.edit_message_text("Настройки сохранены ✅")