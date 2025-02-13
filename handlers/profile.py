async def handle_username_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_username = update.message.text
    if not new_username.startswith("@"):
        new_username = "@" + new_username

    # Обновляем в базе
    await UserRepository.update_username(update.effective_user.id, new_username)
    
    # Уведомляем связанных пользователей (опционально)
    connections = await UserRepository.get_user_connections(update.effective_user.id)
    for conn in connections:
        await context.bot.send_message(
            chat_id=conn.user_id,
            text=f"ℹ️ Пользователь {update.effective_user.full_name} обновил username: {new_username}"
        )