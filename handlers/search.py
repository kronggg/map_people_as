from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from utils.database.core import DatabaseManager

async def search_criteria(update: Update, context: CallbackContext):
    lang = context.user_data.get("language", "RU")
    if lang == "RU":
        await update.message.reply_text("Введите критерий поиска (локация, профессия, навыки, хобби):")
    else:
        await update.message.reply_text("Enter search criteria (location, profession, skills, hobbies):")
    return "SEARCH_CRITERIA"

async def process_search(update: Update, context: CallbackContext):
    criteria = update.message.text.lower()
    lang = context.user_data.get("language", "RU")

    results = await DatabaseManager.fetch_all(
        "SELECT nickname, city, profession, skills, hobbies FROM users WHERE "
        "LOWER(city) LIKE ? OR LOWER(profession) LIKE ? OR LOWER(skills) LIKE ? OR LOWER(hobbies) LIKE ?",
        (f"%{criteria}%", f"%{criteria}%", f"%{criteria}%", f"%{criteria}%"),
    )

    if results:
        response = "\n".join([f"{user[0]} ({user[1]}): Профессия - {user[2]}, Навыки - {user[3]}, Хобби - {user[4]}" for user in results])
    else:
        response = "Никого не найдено." if lang == "RU" else "No users found."

    await update.message.reply_text(response)
    return ConversationHandler.END

def get_search_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("search", search_criteria)],
        states={"SEARCH_CRITERIA": [MessageHandler(filters.TEXT & ~filters.COMMAND, process_search)]},
        fallbacks=[],
    )