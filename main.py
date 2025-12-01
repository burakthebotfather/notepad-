import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ID пользователя, которому пересылаются отметки
TARGET_USER_ID = 542345855

# Чаты и треды, в которых бот работает
allowed_locations = {
    -1002360529455: 3
}

# Триггерный символ
TRIGGER = "+"


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.effective_message
    chat_id = message.chat_id
    thread_id = message.message_thread_id

    # Проверяем, что сообщение из нужного чата + нужного треда
    if chat_id not in allowed_locations:
        return
    if allowed_locations[chat_id] != thread_id:
        return

    text = message.text or ""

    # --- Если сообщение содержит "+"
    if TRIGGER in text:
        await context.bot.forward_message(
            chat_id=TARGET_USER_ID,
            from_chat_id=chat_id,
            message_id=message.message_id
        )
        return

    # --- Если сообщение НЕ содержит "+"
    await message.reply_text(
        "Отметка отклонена. Причина: не обнаружен основной триггер. "
        "Пожалуйста, отправьте отметку повторно новым сообщением."
    )

    # Уведомление админу
    await context.bot.send_message(
        chat_id=TARGET_USER_ID,
        text="❌ *Отклонено*\nСообщение пользователя:",
        parse_mode="Markdown"
    )

    # Пересылаем само сообщение как отклонённое
    await context.bot.forward_message(
        chat_id=TARGET_USER_ID,
        from_chat_id=chat_id,
        message_id=message.message_id
    )


async def main():
    # Читаем токен из Railway → Variables → BOT_TOKEN
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token:
        raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения Railway!")

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
