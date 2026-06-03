import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from db import init_db, add_expense, get_expenses, delete_expense

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


# START
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Hallo 👋\n\n"
        "Ich bin dein Kosten-Kontrolle Bot.\n\n"
        "Befehle:\n"
        "/add 250 Kaffee – Ausgabe hinzufügen\n"
        "/list – alle Ausgaben anzeigen\n"
        "/delete 3 – Ausgabe löschen\n"
        "/help – Hilfe anzeigen"
    )


# HELP
@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Ich kann dir helfen, deine Ausgaben zu verwalten 📊\n\n"
        "Befehle:\n"
        "/add 250 Kaffee\n"
        "/list\n"
        "/delete 3"
    )


# ADD EXPENSE
@dp.message(Command("add"))
async def add_command(message: Message):
    text = message.text or ""
    parts = text.split(maxsplit=2)

    if len(parts) < 3:
        await message.answer("Verwendung: /add 250 Kaffee")
        return

    try:
        amount = float(parts[1])
    except ValueError:
        await message.answer("Bitte gib eine gültige Zahl ein. Beispiel: /add 250 Kaffee")
        return

    description = parts[2]

    await add_expense(message.from_user.id, amount, description)

    await message.answer(f"Gespeichert: {amount} – {description}")


# LIST EXPENSES
@dp.message(Command("list"))
async def list_command(message: Message):
    expenses = await get_expenses(message.from_user.id)

    if not expenses:
        await message.answer("Du hast noch keine Ausgaben gespeichert.")
        return

    text = ["📊 Deine Ausgaben:\n"]
    total = 0

    for index, expense in enumerate(expenses, start=1):
        expense_id, amount, description, created_at = expense

        text.append(
            f"#{index} | {amount} € | {description} | {created_at}"
        )

        total += amount

    text.append(f"\nGesamt: {total} €")

    await message.answer("\n".join(text))


# DELETE EXPENSE
@dp.message(Command("delete"))
async def delete_command(message: Message):
    text = message.text or ""
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Verwendung: /delete 3")
        return

    try:
        index = int(parts[1])
    except ValueError:
        await message.answer("Bitte gib eine gültige ID ein.")
        return

    expenses = await get_expenses(message.from_user.id)

    if index < 1 or index > len(expenses):
        await message.answer(f"Eintrag #{index} existiert nicht.")
        return

    real_id = expenses[index - 1][0]

    await delete_expense(message.from_user.id, real_id)
    await message.answer(f"Eintrag #{index} wurde gelöscht 🗑")


# MAIN
async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN nicht gefunden (.env Datei prüfen)")

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())