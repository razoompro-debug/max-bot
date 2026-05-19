from maxapi import Bot
from collections import defaultdict

TOKEN = "f9LHodD0cOIloCdM4S4u2QEo0hF1yDOLdVH23RWt5jZwWyIWM82UMhtRYvdd5vPJJ4jYfNEjdPrbnSAV4siW"

bot = Bot(TOKEN)

# Хранилище данных пользователей
users = defaultdict(dict)

# Возможные размеры
SIZES = ["S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL", "6XL"]

# Цвета футболок
TSHIRT_COLORS = [
    "Белая",
    "Черная",
    "Красная",
    "Синяя",
    "Зеленая"
]

# Цвета надписей
TEXT_COLORS = [
    "Черный",
    "Белый",
    "Красный",
    "Синий",
    "Золотой"
]


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.chat.id

    users[user_id] = {
        "step": "gender"
    }

    bot.send_message(
        user_id,
        "👕 Добро пожаловать в бот заказа именных футболок!\n\n"
        "Выберите тип футболки:\n"
        "1. Мужская\n"
        "2. Женская"
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    text = message.text

    if user_id not in users:
        users[user_id]["step"] = "gender"

    step = users[user_id].get("step")

    # 1. Мужская / Женская
    if step == "gender":
        if text.lower() in ["мужская", "1"]:
            users[user_id]["gender"] = "Мужская"
        elif text.lower() in ["женская", "2"]:
            users[user_id]["gender"] = "Женская"
        else:
            bot.send_message(user_id, "Введите: Мужская или Женская")
            return

        users[user_id]["step"] = "size"

        bot.send_message(
            user_id,
            "📏 Выберите размер:\n" + ", ".join(SIZES)
        )

    # 2. Размер
    elif step == "size":
        if text.upper() not in SIZES:
            bot.send_message(
                user_id,
                "❌ Неверный размер.\nВведите один из:\n" + ", ".join(SIZES)
            )
            return

        users[user_id]["size"] = text.upper()
        users[user_id]["step"] = "tshirt_color"

        bot.send_message(
            user_id,
            "🎨 Выберите цвет футболки:\n" +
            "\n".join(TSHIRT_COLORS)
        )

    # 3. Цвет футболки
    elif step == "tshirt_color":
        users[user_id]["tshirt_color"] = text
        users[user_id]["step"] = "print_text"

        bot.send_message(
            user_id,
            "✍️ Отправьте надпись для футболки.\n"
            "Если хотите использовать фото надписи — отправьте изображение."
        )

    # 4. Надпись или фото
    elif step == "print_text":

        # Проверяем текст
        if text:
            users[user_id]["print"] = text
            users[user_id]["print_type"] = "Текст"

        users[user_id]["step"] = "text_color"

        bot.send_message(
            user_id,
            "🌈 Выберите цвет надписи:\n" +
            "\n".join(TEXT_COLORS)
        )

    # 5. Цвет надписи
    elif step == "text_color":
        users[user_id]["text_color"] = text
        users[user_id]["step"] = "client_info"

        bot.send_message(
            user_id,
            "📋 Введите данные в формате:\n\n"
            "ФИО\n"
            "Телефон\n"
            "Адрес доставки"
        )

    # 6. Контакты клиента
    elif step == "client_info":
        users[user_id]["client_info"] = text

        order = users[user_id]

        result = f"""
✅ НОВЫЙ ЗАКАЗ

👕 Тип футболки: {order.get('gender')}
📏 Размер: {order.get('size')}
🎨 Цвет футболки: {order.get('tshirt_color')}

✍️ Надпись:
{order.get('print')}

🌈 Цвет надписи:
{order.get('text_color')}

📋 Данные клиента:
{order.get('client_info')}
"""

        bot.send_message(
            user_id,
            result
        )

        # Здесь можно отправлять заказ администратору
        ADMIN_ID = "10878339"

        bot.send_message(
            ADMIN_ID,
            "📦 Новый заказ!\n" + result
        )

        users[user_id]["step"] = "done"

        bot.send_message(
            user_id,
            "🙏 Спасибо за заказ!\n"
            "С вами скоро свяжется менеджер."
        )


print("Бот запущен...")
bot.infinity_polling()