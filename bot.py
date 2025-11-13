import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ParseMode

# --- НАЛАШТУВАННЯ ТОКЕНА ---
# Бот спробує взяти токен із налаштувань сервера (Render).
# Якщо не знайде — візьме той, що в лапках (для тестів на комп'ютері).
TOKEN = "7973360645:AAEg3oGRoz38TjuO2YTuK7z2PgF4xoNccvM"

# Якщо забув додати змінну на Render, бот впаде з помилкою, щоб ти це помітив.
if not TOKEN:
    # Тимчасовий варіант, якщо тестуєш локально, можеш розкоментувати рядок нижче,
    # АЛЕ НЕ ЗАЛИШАЙ ЙОГО ДЛЯ RENDER!
    # TOKEN = "ТВІЙ_ТОКЕН_ВСТАВ_СЮДИ"
    raise ValueError(
        "❌ Помилка: Не знайдено змінну BOT_TOKEN! Додай її в Environment Variables на Render.")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

dp = Dispatcher()

MANAGER_USERNAME = "@magic_support"

builder = ReplyKeyboardBuilder()
builder.button(text="📞 Зв’язатися з менеджером")
builder.button(text="🕓 Запис на консультацію")
# Ти прибрав кнопку адреси в цьому коді, тому я залишаю як є:
builder.adjust(2)
main_menu = builder.as_markup(resize_keyboard=True)

user_states = {}

# --- ХЕНДЛЕРЫ ---


@dp.message(Command("start"))
async def start(message: types.Message):
    user_states.pop(message.from_user.id, None)
    text = (
        "Вітаємо у *Магії прикрас* 💍\n\n"
        "Ми створюємо витончені прикраси, які підкреслюють твою унікальність ✨\n\n"
        "Оберіть дію нижче 👇"
    )
    await message.answer(text, reply_markup=main_menu)


@dp.message(F.text.contains("Зв’язатися з менеджером"))
async def contact_manager(message: types.Message):
    user_states.pop(message.from_user.id, None)
    text = (
        f"Наш менеджер завжди на зв’язку 💬\n\n"
        f"Telegram: {MANAGER_USERNAME}\n"
        "Instagram: @magia_prykras\n\n"
        "Або напишіть свій запит прямо сюди 💎"
    )
    await message.answer(text)


@dp.message(F.text.contains("Запис на консультацію"))
async def start_consultation(message: types.Message):
    user_states[message.from_user.id] = {"step": "name"}
    await message.answer(
        "Чудово! 💫 Для запису на консультацію, спочатку напишіть ваше *ім’я*:"
    )


@dp.message(F.text, F.from_user.id.in_(user_states.keys()))
async def consultation_steps(message: types.Message):
    user_id = message.from_user.id
    state = user_states[user_id]

    if message.text.startswith("/"):
        return

    if state["step"] == "name":
        state["name"] = message.text
        state["step"] = "date"
        await message.answer(
            "Дякую 🌸 Тепер вкажіть, будь ласка, *бажану дату та час консультації*:"
        )
    elif state["step"] == "date":
        state["date"] = message.text
        state["step"] = "topic"
        await message.answer(
            "Добре 💎 Тепер коротко опишіть, *що саме вас цікавить* (наприклад: підбір каблучки, подарунок тощо):"
        )
    elif state["step"] == "topic":
        state["topic"] = message.text
        state["step"] = "contact"
        await message.answer(
            "І нарешті — залиште, будь ласка, *ваш контакт* (телеграм або номер телефону):"
        )
    elif state["step"] == "contact":
        state["contact"] = message.text

        summary = (
            f"📋 *Нова заявка на консультацію!*\n\n"
            f"👤 Ім’я: {state['name']}\n"
            f"📅 Дата: {state['date']}\n"
            f"💬 Тема: {state['topic']}\n"
            f"📞 Контакт: {state['contact']}\n\n"
            f"Заявка від @{message.from_user.username or 'без_нікнейму'}"
        )

        await bot.send_message(
            chat_id=message.chat.id,
            text="✅ Дякуємо! Ваша заявка відправлена менеджеру 💖\nОчікуйте на відповідь протягом дня.",
        )
        await bot.send_message(chat_id=message.chat.id, text=summary)

        del user_states[user_id]


@dp.message()
async def fallback(message: types.Message):
    await message.answer("Не зовсім розумію 😅\nОберіть дію з меню 👇", reply_markup=main_menu)


async def main():
    print("✅ Бот «Магія прикрас» запущено!")

    # --- ВИПРАВЛЕННЯ ТУТ ---
    # Було: await dp.delete_webhook(...) -> Помилка
    # Стало: await bot.delete_webhook(...)
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
