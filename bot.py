from flask import Flask, request, jsonify
import requests
import os
from openpyxl import Workbook, load_workbook
from datetime import datetime

# =========================================
# НАСТРОЙКИ
# =========================================

TOKEN = "f9LHodD0cOIloCdM4S4u2QEo0hF1yDOLdVH23RWt5jZwWyIWM82UMhtRYvdd5vPJJ4jYfNEjdPrbnSAV4siW"

API_URL = "https://platform-api.max.ru"

ADMIN_USER_ID = "10878339"

EXCEL_FILE = "orders.xlsx"

app = Flask(__name__)

# =========================================
# СОЗДАНИЕ EXCEL
# =========================================

def create_excel():

    if not os.path.exists(EXCEL_FILE):

        wb = Workbook()
        ws = wb.active

        ws.title = "Orders"

        ws.append([
            "Дата",
            "User ID",
            "Имя",
            "Телефон",
            "Заказ"
        ])

        wb.save(EXCEL_FILE)

# =========================================
# СОХРАНЕНИЕ ЗАКАЗА
# =========================================

def save_order(user_id, name, phone, order_text):

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    ws.append([
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        user_id,
        name,
        phone,
        order_text
    ])

    wb.save(EXCEL_FILE)

# =========================================
# ОТПРАВКА СООБЩЕНИЯ
# =========================================

def send_message(user_id, text):

    url = f"{API_URL}/messages"

    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }

    data = {
        "recipient": {
            "user_id": user_id
        },
        "message": {
            "text": text
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print("SEND MESSAGE STATUS:", response.status_code)
    print("SEND MESSAGE RESPONSE:", response.text)

# =========================================
# ГЛАВНАЯ СТРАНИЦА
# =========================================

@app.route("/")
def home():
    return "MAX BOT WORKING"

# =========================================
# WEBHOOK
# =========================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("WEBHOOK DATA:", data)

    message = data.get("message", {})

    body = message.get("body", {})

    sender = message.get("sender", {})

    text = body.get("text", "")

    user_name = sender.get("first_name", "Пользователь")

    user_id = sender.get("user_id")

    print("USER ID:", user_id)
    print("TEXT:", text)

    # =====================================
    # /start
    # =====================================

    if text == "/start":

        answer = f"""
Здравствуйте, {user_name}! 👋

Добро пожаловать в бот заказов.

Доступные команды:

/start — запуск
/order — оформить заказ
/help — помощь
"""

        send_message(user_id, answer)

    # =====================================
    # /help
    # =====================================

    elif text == "/help":

        send_message(
            user_id,
            "Напишите:\n/order ваш заказ"
        )

    # =====================================
    # /order
    # =====================================

    elif text.startswith("/order"):

        order_text = text.replace("/order", "").strip()

        if order_text == "":

            send_message(
                user_id,
                "Пример:\n/order Хочу заказать баннер"
            )

        else:

            save_order(
                user_id,
                user_name,
                "Не указан",
                order_text
            )

            send_message(
                user_id,
                f"✅ Заказ принят:\n{order_text}"
            )

            # уведомление админу
            if ADMIN_USER_ID != "":

                send_message(
                    ADMIN_USER_ID,
                    f"""
🆕 Новый заказ

👤 {user_name}
🆔 {user_id}

💬 {order_text}
"""
                )

    # =====================================
    # НЕИЗВЕСТНАЯ КОМАНДА
    # =====================================

    else:

        send_message(
            user_id,
            "Неизвестная команда.\nНапишите /help"
        )

    return jsonify({
        "status": "ok"
    })

# =========================================
# ЗАПУСК
# =========================================

if __name__ == "__main__":

    create_excel()

    app.run(
        host="0.0.0.0",
        port=10000
    )