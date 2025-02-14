from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters

async def choose_language(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="RU")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="EN")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите язык / Choose language:", reply_markup=reply_markup)
    return "SET_LANGUAGE"

async def set_language(update: Update, context: CallbackContext):
    query = update.callback_query
    language = query.data
    context.user_data["language"] = language
    await query.answer("Язык установлен!")
    await query.edit_message_text("Язык установлен!" if language == "RU" else "Language set!")
    return ConversationHandler.END

def get_language_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("language", choose_language)],
        states={"SET_LANGUAGE": [CallbackQueryHandler(set_language)]},
        fallbacks=[],
    )