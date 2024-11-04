#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
import logging
from typing import Dict

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Словарь для хранения заметок
notes = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот для заметок. Вы можете добавлять, удалять и просматривать заметки.\n\n"
        "Команды:\n"
        "/add <категория> <текст заметки> - добавить заметку\n"
        "/delete <категория> <номер заметки> - удалить заметку\n"
        "/view <категория> - просмотреть заметки в категории\n"
        "/view_all - просмотреть все заметки"
    )

# Команда /add для добавления заметки
async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        notes['Без категории'] = context.args[0]
        await update.message.reply_text(f"Заметка добавлена в категорию 'Без_категории'.")
        return

    category = context.args[0]
    note_text = ' '.join(context.args[1:])

    if category not in notes:
        notes[category] = []

    notes[category].append(note_text)
    await update.message.reply_text(f"Заметка добавлена в категорию '{category}'.")

# Команда /delete для удаления заметки
async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /delete <категория> <номер заметки>")
        return

    category = context.args[0]
    try:
        note_index = int(context.args[1]) - 1
    except ValueError:
        await update.message.reply_text("Номер заметки должен быть числом.")
        return

    if category in notes and 0 <= note_index < len(notes[category]):
        deleted_note = notes[category].pop(note_index)
        await update.message.reply_text(f"Заметка удалена из категории '{category}': {deleted_note}")
    else:
        await update.message.reply_text("Заметка не найдена. Проверьте категорию и номер заметки.")

# Команда /view для просмотра заметок в одной категории
async def view_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /view <категория>")
        return

    category = context.args[0]
    if category in notes and notes[category]:
        message = f"Заметки в категории '{category}':\n"
        for i, note in enumerate(notes[category], start=1):
            message += f"{i}. {note}\n"
    else:
        message = f"В категории '{category}' пока нет заметок."
    
    await update.message.reply_text(message)

# Команда /view_all для просмотра всех заметок
async def view_all_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not notes:
        await update.message.reply_text("Заметок пока нет.")
        return

    message = "Все заметки:\n"
    for category, category_notes in notes.items():
        message += f"\nКатегория '{category}':\n"
        for i, note in enumerate(category_notes, start=1):
            message += f"{i}. {note}\n"
    
    await update.message.reply_text(message)
"""
async def view_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not notes:
        await update.message.reply_text("Заметок пока нет.")
        return

    message = "Все категории:\n"
    for category, category_notes in notes.keys():
        message += f"\n{category}'\n"
    
    await update.message.reply_text(message)
"""
async def post_init(application: Application) -> None:
    bot_commands = [
        BotCommand("start", "Начало работы с ботом"),
        BotCommand("add", 'Добавь заметку'),
        BotCommand('delete','Удали заметку'),
        BotCommand('view', 'Покажи заметки в данной категории'),
        BotCommand('view_all', 'Покажи все, что есть!')
        #BotCommand('categories', 'А какие категории вообще есть.')
    ]
    await application.bot.set_my_commands(bot_commands)

# Основной код для запуска бота
def main():
    persistence = PicklePersistence(filepath="data/data", single_file=False)
    application = Application.builder().token(os.getenv("BOT_TOKEN")).persistence(persistence).post_init(post_init).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_note))
    application.add_handler(CommandHandler("delete", delete_note))
    application.add_handler(CommandHandler("view", view_notes))
    application.add_handler(CommandHandler("view_all", view_all_notes))
    #application.add_handler(CommandHandler("categories", view_categories))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
