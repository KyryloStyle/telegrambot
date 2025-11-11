from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio

# 🔐 ВСТАВ СВІЙ ТОКЕН
TOKEN = "7973360645:AAEg3oGRoz38TjuO2YTuK7z2PgF4xoNccvM"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔹 Менеджер магазину
MANAGER_USERNAME = "@magic_support"  # контакт менеджера «Магія прикрас»

# 📱 Головне меню
builder = ReplyKeyboardBuilder()
builder.button(text="💎 Наші колекції")
builder.button(text="📞 Зв’язатися з менеджером")
builder.button(text="🕓 Запис на консультацію")
builder.button(text="🎁 Спеціальні пропозиції")
builder.adjust(2, 2)
main_menu = builder.as_markup(resize_keyboard=True)

# 📋 Зберігаємо тимчасовий стан користувача
user_states = {}


@dp.message(Command("start"))
async def start(message: types.Message):
    text = (
        "Вітаємо у *Магії прикрас* 💍\n\n"
        "Ми створюємо витончені прикраси, які підкреслюють твою унікальність ✨\n\n"
        "Оберіть дію нижче 👇"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu)


# === 💎 Колекції ===
@dp.message(F.text == "💎 Наші колекції")
async def collections(message: types.Message):
    await message.answer(
        "Наші найпопулярніші колекції:\n"
        "✨ *Aurora* — класика з блиском\n"
        "🌸 *Blossom* — весняна ніжність\n"
        "🌙 *Luna* — мінімалізм і сучасність\n\n"
        f"Щоб побачити фото — напишіть нашому менеджеру {MANAGER_USERNAME}",
        parse_mode="Markdown",
    )


# === 📞 Контакти ===
@dp.message(F.text == "📞 Зв’язатися з менеджером")
async def contact_manager(message: types.Message):
    await message.answer(
        f"Наш менеджер завжди на зв’язку 💬\n\n"
        f"Telegram: {MANAGER_USERNAME}\n"
        "Instagram: @magia_prykras\n\n"
        "Або напишіть свій запит прямо сюди 💎",
        parse_mode="Markdown",
    )


# === 🕓 Запис на консультацію ===
@dp.message(F.text == "🕓 Запис на консультацію")
async def start_consultation(message: types.Message):
    user_states[message.from_user.id] = {"step": "name"}
    await message.answer("Чудово! 💫 Для запису на консультацію, спочатку напишіть ваше *ім’я*:", parse_mode="Markdown")


@dp.message(F.text, F.from_user.id.in_(user_states.keys()))
async def consultation_steps(message: types.Message):
    user_id = message.from_user.id
    state = user_states[user_id]

    # Крок 1 — Ім’я
    if state["step"] == "name":
        state["name"] = message.text
        state["step"] = "date"
        await message.answer("Дякую 🌸 Тепер вкажіть, будь ласка, *бажану дату та час консультації*:", parse_mode="Markdown")

    # Крок 2 — Дата
    elif state["step"] == "date":
        state["date"] = message.text
        state["step"] = "topic"
        await message.answer("Добре 💎 Тепер коротко опишіть, *що саме вас цікавить* (наприклад: підбір каблучки, подарунок тощо):", parse_mode="Markdown")

    # Крок 3 — Тема консультації
    elif state["step"] == "topic":
        state["topic"] = message.text
        state["step"] = "contact"
        await message.answer("І нарешті — залиште, будь ласка, *ваш контакт* (телеграм або номер телефону):", parse_mode="Markdown")

    # Крок 4 — Контакт
    elif state["step"] == "contact":
        state["contact"] = message.text

        # Формуємо заявку
        name = state["name"]
        date = state["date"]
        topic = state["topic"]
        contact = state["contact"]

        summary = (
            f"📋 *Нова заявка на консультацію!*\n\n"
            f"👤 Ім’я: {name}\n"
            f"📅 Дата: {date}\n"
            f"💬 Тема: {topic}\n"
            f"📞 Контакт: {contact}\n\n"
            f"Заявка від @{message.from_user.username or 'без_нікнейму'}"
        )

        # Надсилаємо менеджеру
        await bot.send_message(chat_id=message.chat.id, text="✅ Дякуємо! Ваша заявка відправлена менеджеру 💖\nОчікуйте на відповідь протягом дня.")
        await bot.send_message(chat_id=MANAGER_USERNAME, text=summary, parse_mode="Markdown")

        del user_states[user_id]


# === 🎁 Акції ===
@dp.message(F.text == "🎁 Спеціальні пропозиції")
async def special_offers(message: types.Message):
    await message.answer(
        "🎁 *Спеціальна пропозиція тижня!*\n\n"
        "Знижка -20% на колекцію *Luna* 🌙\n"
        "Акція діє до кінця тижня ✨\n\n"
        f"Детальніше у менеджера {MANAGER_USERNAME}",
        parse_mode="Markdown",
    )


# === На інші повідомлення ===
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Не зовсім розумію 😅\nОберіть дію з меню 👇", reply_markup=main_menu)


async def main():
    print("✅ Бот «Магія прикрас» запущено!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
