import os
from datetime import datetime

from flask import Flask, request, jsonify
import requests

from openpyxl import Workbook, load_workbook

# =========================================
# НАСТРОЙКИ
# =========================================

TOKEN = os.getenv("f9LHodD0cOJmCYW9DutFVo0epU2vwCwD0su7gmhyLdUR1ZJ2zOx6yEVlyyUjQ5l0oWxMPNllo1sujLw218Vy")

API_URL = "https://platform-api.max.ru"

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

EXCEL_FILE = "orders.xlsx"

app = Flask(__name__)

# =========================================
# EXCEL
# =========================================

def create_excel():

    if not os.path.exists(EXCEL_FILE):

        wb = Workbook()
        ws = wb.active

        ws.title = "Orders"

        ws.append([
            "Дата",
            "Модель",
            "Размер",
            "Цвет футболки",
            "Надпись",
            "Цвет надписи",
            "Размер надписи",
            "ФИО",
            "Телефон",
            "Адрес"
        ])

        wb.save(EXCEL_FILE)

create_excel()

# =========================================
# СОХРАНЕНИЕ ЗАКАЗА
# =========================================

def save_order(data):

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    ws.append([
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        data.get("gender"),
        data.get("size"),
        data.get("tshirt_color"),
        data.get("text"),
        data.get("text_color"),
        data.get("text_size"),
        data.get("name"),
        data.get("phone"),
        data.get("address")
    ])

    wb.save(EXCEL_FILE)

# =========================================
# ПАМЯТЬ ПОЛЬЗОВАТЕЛЕЙ
# =========================================

users = {}

# =========================================
# ОТПРАВКА СООБЩЕНИЯ
# =========================================

def send_message(chat_id, text):

    url = f"{API_URL}/messages"

    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "chatId": chat_id,
        "text": text
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print(response.text)

# =========================================
# WEBHOOK
# =========================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print(data)

    try:

        message = data.get("message")

        if not message:
            return jsonify({"ok": True})

        chat_id = message["chat"]["chatId"]

        user_id = str(message["from"]["userId"])

        text = message.get("text", "")

        # =====================================
        # START
        # =====================================

        if text == "/start":

            users[user_id] = {
                "step": "gender"
            }

            send_message(
                chat_id,
                "👕 Именные футболки\n\n"
                "Выберите модель:\n\n"
                "1 - Мужская\n"
                "2 - Женская"
            )

            return jsonify({"ok": True})

        # =====================================
        # ПРОВЕРКА
        # =====================================

        if user_id not in users:

            send_message(
                chat_id,
                "Напишите /start"
            )

            return jsonify({"ok": True})

        user = users[user_id]

        step = user["step"]

        # =====================================
        # МОДЕЛЬ
        # =====================================

        if step == "gender":

            if text == "1":
                user["gender"] = "Мужская"

            elif text == "2":
                user["gender"] = "Женская"

            else:

                send_message(
                    chat_id,
                    "Введите 1 или 2"
                )

                return jsonify({"ok": True})

            user["step"] = "size"

            send_message(
                chat_id,
                "📏 Размер:\n\n"
                "1 - MINI\n"
                "2 - MAXI"
            )

            return jsonify({"ok": True})

        # =====================================
        # РАЗМЕР
        # =====================================

        if step == "size":

            if text == "1":
                user["size"] = "MINI"

            elif text == "2":
                user["size"] = "MAXI"

            else:

                send_message(
                    chat_id,
                    "Введите 1 или 2"
                )

                return jsonify({"ok": True})

            user["step"] = "tshirt_color"

            send_message(
                chat_id,
                "🎨 Цвет футболки:\n\n"
                "1 - Белый\n"
                "2 - Чёрный\n"
                "3 - Красный\n"
                "4 - Синий"
            )

            return jsonify({"ok": True})

        # =====================================
        # ЦВЕТ ФУТБОЛКИ
        # =====================================

        if step == "tshirt_color":

            colors = {
                "1": "Белый",
                "2": "Чёрный",
                "3": "Красный",
                "4": "Синий"
            }

            if text not in colors:

                send_message(
                    chat_id,
                    "Введите число от 1 до 4"
                )

                return jsonify({"ok": True})

            user["tshirt_color"] = colors[text]

            user["step"] = "text"

            send_message(
                chat_id,
                "✍️ Введите текст надписи:"
            )

            return jsonify({"ok": True})

        # =====================================
        # ТЕКСТ
        # =====================================

        if step == "text":

            user["text"] = text

            user["step"] = "text_color"

            send_message(
                chat_id,
                "🎨 Цвет надписи:\n\n"
                "1 - Белый\n"
                "2 - Чёрный\n"
                "3 - Красный\n"
                "4 - Золотой"
            )

            return jsonify({"ok": True})

        # =====================================
        # ЦВЕТ НАДПИСИ
        # =====================================

        if step == "text_color":

            colors = {
                "1": "Белый",
                "2": "Чёрный",
                "3": "Красный",
                "4": "Золотой"
            }

            if text not in colors:

                send_message(
                    chat_id,
                    "Введите число от 1 до 4"
                )

                return jsonify({"ok": True})

            user["text_color"] = colors[text]

            user["step"] = "text_size"

            send_message(
                chat_id,
                "📏 Размер надписи:\n\n"
                "1 - Маленькая\n"
                "2 - Средняя\n"
                "3 - Большая"
            )

            return jsonify({"ok": True})

        # =====================================
        # РАЗМЕР НАДПИСИ
        # =====================================

        if step == "text_size":

            sizes = {
                "1": "Маленькая",
                "2": "Средняя",
                "3": "Большая"
            }

            if text not in sizes:

                send_message(
                    chat_id,
                    "Введите число от 1 до 3"
                )

                return jsonify({"ok": True})

                user["text_size"] = sizes[text]

            user["text_size"] = sizes[text]

            user["step"] = "name"

            send_message(
                chat_id,
                "👤 Введите ФИО:"
            )

            return jsonify({"ok": True})

        # =====================================
        # ФИО
        # =====================================

        if step == "name":

            user["name"] = text

            user["step"] = "phone"

            send_message(
                chat_id,
                "📱 Введите номер телефона:"
            )

            return jsonify({"ok": True})

        # =====================================
        # ТЕЛЕФОН
        # =====================================

        if step == "phone":

            user["phone"] = text

            user["step"] = "address"

            send_message(
                chat_id,
                "🏠 Введите адрес доставки:"
            )

            return jsonify({"ok": True})

        # =====================================
        # АДРЕС
        # =====================================

        if step == "address":

            user["address"] = text

            save_order(user)

            order_text = f"""
НОВЫЙ ЗАКАЗ

👔 Модель: {user['gender']}
📏 Размер: {user['size']}

🎨 Цвет футболки: {user['tshirt_color']}

✍️ Надпись: {user['text']}
🎨 Цвет надписи: {user['text_color']}
📏 Размер надписи: {user['text_size']}

👤 ФИО: {user['name']}
📱 Телефон: {user['phone']}
🏠 Адрес: {user['address']}
"""

            # КЛИЕНТУ

            send_message(
                chat_id,
                "✅ Спасибо за заказ!\n\n"
                "Наш менеджер скоро свяжется с вами ✨"
            )

            # АДМИНУ

            if ADMIN_CHAT_ID:

                send_message(
                    ADMIN_CHAT_ID,
                    order_text
                )

            del users[user_id]

            return jsonify({"ok": True})

    except Exception as e:

        print("ERROR:", e)

    return jsonify({"ok": True})

# =========================================
# ГЛАВНАЯ
# =========================================

@app.route("/")
def home():

    return "MAX BOT WORKING"

# =========================================
# ЗАПУСК
# =========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )