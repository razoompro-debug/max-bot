from flask import Flask, request, jsonify
import requests
import os
import time
from openpyxl import Workbook, load_workbook
from datetime import datetime

# =========================================
# НАСТРОЙКИ
# =========================================

TOKEN = "f9LHodD0cOIloCdM4S4u2QEo0hF1yDOLdVH23RWt5jZwWyIWM82UMhtRYvdd5vPJJ4jYfNEjdPrbnSAV4siW"

API_URL = "https://platform-api.max.ru"

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
            "Заказ"
        ])

        wb.save(EXCEL_FILE)

        print("EXCEL CREATED")

# =========================================
# СОХРАНЕНИЕ ЗАКАЗА
# =========================================

def save_order(user_id, name, order_text):

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    ws.append([
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        user_id,
        name,
        order_text
    ])

    wb.save(EXCEL_FILE)

    print("ORDER SAVED")

# =========================================
# ОТПРАВКА СООБЩЕНИЯ
# =========================================

def send_message(user_id, text):

    print("=================================")
    print("SEND MESSAGE")
    print("USER:", user_id)

    url = f"{API_URL}/messages"

    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "recipient": {
            "user_id": int(user_id)
        },
        "message": {
            "text": text
        }
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=15
        )

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        # =================================
        # RATE LIMIT
        # =================================

        if response.status_code == 429:

            print("RATE LIMIT - WAIT 2 SEC")

            time.sleep(2)

        print("=================================")

    except Exception as e:

        print("SEND ERROR:", str(e))

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

    try:

        data = request.json

        print("WEBHOOK DATA:", data)

        # =====================================
        # BOT STARTED
        # =====================================

        if data.get("update_type") == "bot_started":

            print("BOT STARTED EVENT")

            return jsonify({
                "status": "ok"
            })

        # =====================================
        # MESSAGE
        # =====================================

        message = data.get("message")

        if not message:

            print("NO MESSAGE")

            return jsonify({
                "status": "no_message"
            })

        body = message.get("body", {})
        sender = message.get("sender", {})

        text = body.get("text", "").strip()

        user_id = sender.get("user_id")

        user_name = sender.get(
            "first_name",
            "Пользователь"
        )

        print("USER ID:", user_id)
        print("TEXT:", text)

        if not user_id:

            print("NO USER ID")

            return jsonify({
                "status": "no_user_id"
            })

        # =====================================
        # /start
        # =====================================

        if text == "/start":

            answer = f"""
Здравствуйте, {user_name}! 👋

Добро пожаловать в бот заказов.

Доступные команды:

/start — запуск
/help — помощь
/order — оформить заказ

Пример:

/order Хочу заказать баннер
"""

            send_message(user_id, answer)

        # =====================================
        # /help
        # =====================================

        elif text == "/help":

            send_message(
                user_id,
                """
Напишите:

/order ваш заказ

Пример:

/order Хочу заказать баннер
"""
            )

        # =====================================
        # /order
        # =====================================

        elif text.startswith("/order"):

            order_text = text.replace(
                "/order",
                ""
            ).strip()

            # пустой заказ
            if order_text == "":

                send_message(
                    user_id,
                    """
Пример:

/order Хочу заказать баннер
"""
                )

            else:

                # сохраняем заказ
                save_order(
                    user_id,
                    user_name,
                    order_text
                )

                # сообщение пользователю
                send_message(
                    user_id,
                    f"""
✅ Заказ принят!

Ваш заказ:

{order_text}
"""
                )

        # =====================================
        # НЕИЗВЕСТНАЯ КОМАНДА
        # =====================================

        else:

            send_message(
                user_id,
                """
Неизвестная команда.

/help
"""
            )

        return jsonify({
            "status": "ok"
        })

    except Exception as e:

        print("WEBHOOK ERROR:", str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        })

# =========================================
# ЗАПУСК
# =========================================

if __name__ == "__main__":

    create_excel()

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )