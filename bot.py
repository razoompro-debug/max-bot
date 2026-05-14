from flask import Flask, request, jsonify
import requests
import os
from openpyxl import Workbook, load_workbook

# =========================================
# НАСТРОЙКИ
# =========================================

TOKEN = "f9LHodD0cOIloCdM4S4u2QEo0hF1yDOLdVH23RWt5jZwWyIWM82UMhtRYvdd5vPJJ4jYfNEjdPrbnSAV4siW"

API_URL = "https://platform-api.max.ru"

ADMIN_CHAT_ID = ""

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
            "Chat ID",
            "Имя",
            "Телефон",
            "Заказ"
        ])

        wb.save(EXCEL_FILE)

# =========================================
# СОХРАНЕНИЕ ЗАКАЗА
# =========================================

def save_order(chat_id, name, phone, order_text):

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    from datetime import datetime

    ws.append([
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        chat_id,
        name,
        phone,
        order_text
    ])

    wb.save(EXCEL_FILE)

# =========================================
# ОТПРАВКА СООБЩЕНИЯ
# =========================================

def send_message(chat_id, text):

    url = f"{API_URL}/messages"

    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }

    data = {
        "chat_id": chat_id,
        "text": text
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

    recipient = message.get("recipient", {})

    chat_id = recipient.get("chat_id")

    text = body.get("text", "")

    user_name = sender.get("first_name", "Пользователь")

    user_id = sender.get("user_id")

    print("CHAT ID:", chat_id)
    print("USER ID:", user_id)
    print("TEXT:", text)

    # =====================================
    # КОМАНДА START
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

        send_message(chat_id, answer)

    # =====================================
    # ПОМОЩЬ
    # =====================================

    elif text == "/help":

        send_message(
            chat_id,
            "Напишите /order чтобы оформить заказ."
        )

    # =====================================
    # ЗАКАЗ
    # =====================================

    elif text.startswith("/order"):

        order_text = text.replace("/order", "").strip()

        if order_text == "":

            send_message(
                chat_id,
                "Пример:\n/order Хочу заказать баннер"
            )

        else:

            save_order(
                chat_id,
                user_name,
                "Не указан",
                order_text
            )

            send_message(
                chat_id,
                f"✅ Заказ принят:\n{order_text}"
            )

            if ADMIN_CHAT_ID != "":

                send_message(
                    ADMIN_CHAT_ID,
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
            chat_id,
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