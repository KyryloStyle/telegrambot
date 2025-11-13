import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ParseMode  # <-- добавили это

TOKEN = "7973360645:AAEg3oGRoz38TjuO2YTuK7z2PgF4xoNccvM"

bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)  # <-- теперь правильно
dp = Dispatcher()

MANAGER_USERNAME = "@magic_support"

builder = ReplyKeyboardBuilder()
builder.button(text="💎 Наші колекції")
builder.button(text="📞 Зв’язатися з менеджером")
builder.button(text="🕓 Запис на консультацію")
builder.button(text="🎁 Спеціальні пропозиції")
builder.adjust(2, 2)
main_menu = builder.as_markup(resize_keyboard=True)

user_states = {}


@dp.message(Command("start"))
async def start(message: types.Message):
    text = (
        "Вітаємо у *Магії прикрас* 💍\n\n"
        "Ми створюємо витончені прикраси, які підкреслюють твою унікальність ✨\n\n"
        "Оберіть дію нижче 👇"
    )
    await message.answer(text, reply_markup=main_menu)


@dp.message(F.text.contains("Наші колекції"))
async def collections(message: types.Message):
    text = (
        "Наші найпопулярніші колекції:\n"
        "✨ *Aurora* — класика з блиском\n"
        "🌸 *Blossom* — весняна ніжність\n"
        "🌙 *Luna* — мінімалізм і сучасність\n\n"
        f"Щоб побачити фото — напишіть нашому менеджеру {MANAGER_USERNAME}"
    )
    await message.answer(text)


@dp.message(F.text.contains("Зв’язатися з менеджером"))
async def contact_manager(message: types.Message):
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
        name = state["name"]
        date = state["date"]
        topic = state["topic"]
        contact = state["contact"]
        username = message.from_user.username or "без_нікнейму"

        summary = (
            f"📋 *Нова заявка на консультацію!*\n\n"
            f"👤 Ім’я: {name}\n"
            f"📅 Дата: {date}\n"
            f"💬 Тема: {topic}\n"
            f"📞 Контакт: {contact}\n\n"
            f"Заявка від @{username}"
        )

        await bot.send_message(
            chat_id=message.chat.id,
            text="✅ Дякуємо! Ваша заявка відправлена менеджеру 💖\nОчікуйте на відповідь протягом дня.",
        )
        await bot.send_message(chat_id=message.chat.id, text=summary)
        del user_states[user_id]


@dp.message(F.text.contains("Спеціальні пропозиції"))
async def special_offers(message: types.Message):
    text = (
        "🎁 *Спеціальна пропозиція тижня!*\n\n"
        "Знижка -20% на колекцію *Luna* 🌙\n"
        "Акція діє до кінця тижня ✨\n\n"
        f"Детальніше у менеджера {MANAGER_USERNAME}"
    )
    await message.answer(text)


@dp.message()
async def fallback(message: types.Message):
    await message.answer("Не зовсім розумію 😅\nОберіть дію з меню 👇", reply_markup=main_menu)


async def main():
    print("✅ Бот «Магія прикрас» запущено!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
