from flask import Flask, request, jsonify
import requests
import os
from openpyxl import Workbook, load_workbook
from datetime import datetime

# ==================================================
# НАСТРОЙКИ
# ==================================================

TOKEN = "f9LHodD0cOIloCdM4S4u2QEo0hF1yDOLdVH23RWt5jZwWyIWM82UMhtRYvdd5vPJJ4jYfNEjdPrbnSAV4siW"

API_URL = "https://platform-api.max.ru"

ADMIN_CHAT_ID = 413483728

EXCEL_FILE = "orders.xlsx"

app = Flask(__name__)

# ==================================================
# СОЗДАНИЕ EXCEL
# ==================================================

def create_excel():

    if not os.path.exists(EXCEL_FILE):

        wb = Workbook()
        ws = wb.active

        ws.title = "Orders"

        ws.append([
            "Дата",
            "Chat ID",
            "Имя",
            "Заказ"
        ])

        wb.save(EXCEL_FILE)

# ==================================================
# СОХРАНЕНИЕ ЗАКАЗА
# ==================================================

def save_order(chat_id, name, order_text):

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    ws.append([
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        chat_id,
        name,
        order_text
    ])

    wb.save(EXCEL_FILE)

# ==================================================
# ОТПРАВКА СООБЩЕНИЯ В MAX
# ==================================================

import time

def send_message(chat_id, text):

    time.sleep(1)

    url = f"{API_URL}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "recipient": {
            "chat_id": int(chat_id)
        },
        "message": {
            "text": text
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print("===================================")
    print("SEND MESSAGE")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
    print("===================================")

    except Exception as e:

        print("SEND ERROR:", str(e))

# ==================================================
# ГЛАВНАЯ СТРАНИЦА
# ==================================================

@app.route("/")
def home():
    return "MAX BOT WORKING"

# ==================================================
# WEBHOOK
# ==================================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("WEBHOOK DATA:", data)

    # сообщение
    message = data.get("message", {})

    # текст
    body = message.get("body", {})
    text = body.get("text", "")

    # пользователь
    sender = message.get("sender", {})
    user_name = sender.get("first_name", "Пользователь")

    # чат
    recipient = message.get("recipient", {})
    chat_id = recipient.get("chat_id")

    print("CHAT ID:", chat_id)
    print("TEXT:", text)

    # ==========================================
    # /start
    # ==========================================

    if text == "/start":

        answer = f"""
👋 Здравствуйте, {user_name}!

Добро пожаловать в бот заказов.

Доступные команды:

/start — запуск
/help — помощь
/order — оформить заказ

Пример заказа:

/order Хочу заказать баннер
"""

        send_message(chat_id, answer)

    # ==========================================
    # /help
    # ==========================================

    elif text == "/help":

        send_message(
            chat_id,
            "Напишите:\n/order ваш заказ"
        )

    # ==========================================
    # /order
    # ==========================================

    elif text.startswith("/order"):

        order_text = text.replace("/order", "").strip()

        # если пусто
        if order_text == "":

            send_message(
                chat_id,
                "Пример:\n/order Хочу заказать баннер"
            )

        else:

            # сохраняем заказ
            save_order(
                chat_id,
                user_name,
                order_text
            )

            # ответ пользователю
            send_message(
                chat_id,
                f"""
✅ Заказ принят!

Ваш заказ:

{order_text}
"""
            )

            # уведомление админу
            send_message(
                ADMIN_CHAT_ID,
                f"""
🆕 Новый заказ

👤 Клиент: {user_name}

💬 Заказ:
{order_text}

🆔 Chat ID:
{chat_id}
"""
            )

    # ==========================================
    # НЕИЗВЕСТНАЯ КОМАНДА
    # ==========================================

    else:

        send_message(
            chat_id,
            "❌ Неизвестная команда.\nНапишите /help"
        )

    return jsonify({
        "status": "ok"
    })

# ==================================================
# ЗАПУСК
# ==================================================

if __name__ == "__main__":

    create_excel()

    app.run(
        host="0.0.0.0",
        port=10000
    )