from aiogram.client.default import DefaultBotProperties
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ParseMode

# Не забудь вернуть переменную окружения, если деплоишь!
TOKEN = "7973360645:AAEg3oGRoz38TjuO2YTuK7z2PgF4xoNccvM"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

dp = Dispatcher()

MANAGER_USERNAME = "@magic_support"

builder = ReplyKeyboardBuilder()
builder.button(text="📞 Зв’язатися з менеджером")
builder.button(text="🕓 Запис на консультацію")
builder.button(text="📍 Адреса магазину")
builder.adjust(2, 1)
main_menu = builder.as_markup(resize_keyboard=True)

user_states = {}

# --- ХЕНДЛЕРЫ (Порядок важен!) ---


@dp.message(Command("start"))
async def start(message: types.Message):
    # Если пользователь перезапускает бота, очищаем его старые состояния
    user_states.pop(message.from_user.id, None)

    text = (
        "Вітаємо у *Магії прикрас* 💍\n\n"
        "Ми створюємо витончені прикраси, які підкреслюють твою унікальність ✨\n\n"
        "Оберіть дію нижче 👇"
    )
    await message.answer(text, reply_markup=main_menu)


# ✅ ИСПРАВЛЕНО: Хендлеры кнопок меню стоят ВЫШЕ, чем steps
# Это гарантирует, что кнопка сработает, даже если бот ждет ввода имени

@dp.message(F.text.contains("Зв’язатися з менеджером"))
async def contact_manager(message: types.Message):
    # Сбрасываем диалог, если он был
    user_states.pop(message.from_user.id, None)

    text = (
        f"Наш менеджер завжди на зв’язку 💬\n\n"
        f"Telegram: {MANAGER_USERNAME}\n"
        "Instagram: @magia_prykras\n\n"
        "Або напишіть свій запит прямо сюди 💎"
    )
    await message.answer(text)


@dp.message(F.text.contains("Адреса магазину"))
async def shop_address(message: types.Message):
    # Сбрасываем диалог, если он был
    user_states.pop(message.from_user.id, None)

    text = (
        "🏠 *Адреса нашого магазину:*\n\n"
        "📍 м. Київ, вул. Хрещатик, 22\n"
        "🕓 Графік роботи: Пн–Нд, 10:00–20:00\n\n"
        f"Зв’яжіться з нами: {MANAGER_USERNAME}"
    )
    await message.answer(text)


@dp.message(F.text.contains("Запис на консультацію"))
async def start_consultation(message: types.Message):
    user_states[message.from_user.id] = {"step": "name"}
    await message.answer(
        "Чудово! 💫 Для запису на консультацію, спочатку напишіть ваше *ім’я*:"
    )


# ✅ Этот хендлер ловит ЛЮБОЙ текст, но только если юзер есть в базе states.
# Он стоит ниже кнопок, поэтому если юзер нажмет кнопку меню — сработают хендлеры выше.
@dp.message(F.text, F.from_user.id.in_(user_states.keys()))
async def consultation_steps(message: types.Message):
    user_id = message.from_user.id
    state = user_states[user_id]

    # Проверка на всякий случай, если вдруг проскочит системная команда
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

        # Формируем отчет
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
        # Тут можно отправить сообщение админу, а не юзеру, если нужно
        await bot.send_message(chat_id=message.chat.id, text=summary)

        # ✅ ВАЖНО: Удаляем пользователя из стейта после завершения
        del user_states[user_id]


@dp.message()
async def fallback(message: types.Message):
    await message.answer("Не зовсім розумію 😅\nОберіть дію з меню 👇", reply_markup=main_menu)


async def main():
    print("✅ Бот «Магія прикрас» запущено!")
    # Очистка очереди старых команд
    await dp.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
