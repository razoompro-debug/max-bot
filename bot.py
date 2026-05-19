from flask import Flask, request, jsonify
import requests
import os
import time
from datetime import datetime
from openpyxl import Workbook, load_workbook

# =====================================================
# НАСТРОЙКИ
# =====================================================

TOKEN = "f9LHodD0cOIloCdM4S4u2QEo0hF1yDOLdVH23RWt5jZwWyIWM82UMhtRYvdd5vPJJ4jYfNEjdPrbnSAV4siW"

# ПРАВИЛЬНЫЙ API
API_URL = "https://botapi.max.ru"

# Excel файл
EXCEL_FILE = "orders.xlsx"

app = Flask(__name__)

# =====================================================
# СОЗДАНИЕ EXCEL
# =====================================================


def create_excel():
    try:
        if not os.path.exists(EXCEL_FILE):
            wb = Workbook()
            ws = wb.active
            ws.title = "Orders"

            ws.append([
                "Дата",
                "User ID",
                "Имя",
                "Сообщение"
            ])

            wb.save(EXCEL_FILE)
            print("EXCEL CREATED")

    except Exception as e:
        print("CREATE EXCEL ERROR:", e)


# =====================================================
# СОХРАНЕНИЕ СООБЩЕНИЙ
# =====================================================


def save_message(user_id, name, text):
    try:
        create_excel()

        wb = load_workbook(EXCEL_FILE)
        ws = wb.active

        ws.append([
            datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            str(user_id),
            str(name),
            str(text)
        ])

        wb.save(EXCEL_FILE)

        print("MESSAGE SAVED")

    except Exception as e:
        print("SAVE ERROR:", e)


# =====================================================
# ОТПРАВКА СООБЩЕНИЯ
# =====================================================


def send_message(chat_id, text):
    try:

        print("=" * 40)
        print("SEND MESSAGE")
        print("CHAT:", chat_id)

        # ПРАВИЛЬНЫЙ URL
        url = f"{API_URL}/messages"

        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "chat_id": int(chat_id),
            "text": str(text)
        }

        time.sleep(1)

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print("=" * 40)

    except Exception as e:
        print("SEND ERROR:", e)


# =====================================================
# ГЛАВНАЯ
# =====================================================


@app.route("/")
def home():
    return "MAX BOT WORKING"


# =====================================================
# WEBHOOK
# =====================================================


@app.route("/webhook", methods=["POST"])
def webhook():
    try:

        data = request.json

        print("WEBHOOK DATA:", data)

        # =============================================
        # СОБЫТИЕ ЗАПУСКА БОТА
        # =============================================

        if data.get("update_type") == "bot_started":
            print("BOT STARTED EVENT")
            return jsonify({"status": "ok"})

        message = data.get("message", {})

        if not message:
            return jsonify({"status": "no_message"})

        body = message.get("body", {})
        sender = message.get("sender", {})
        recipient = message.get("recipient", {})

        # USER ID
        user_id = sender.get("user_id")

        # CHAT ID
        chat_id = recipient.get("chat_id")

        # TEXT
        text = body.get("text", "")

        # NAME
        first_name = sender.get("first_name", "")
        last_name = sender.get("last_name", "")

        user_name = f"{first_name} {last_name}".strip()

        print("USER ID:", user_id)
        print("CHAT ID:", chat_id)
        print("TEXT:", text)

        # сохраняем сообщение
        if text:
            save_message(user_id, user_name, text)

        # =============================================
        # КОМАНДА START
        # =============================================

        if text == "/start":

            answer = f"""
Здравствуйте, {user_name}! 👋

Добро пожаловать в MAX BOT.

Команды:

/start — запуск
/help — помощь
/order — оформить заказ

Пример:
/order Хочу заказать футболку
"""

            send_message(chat_id, answer)

        # =============================================
        # HELP
        # =============================================

        elif text == "/help":

            answer = """
Доступные команды:

/start — запуск
/help — помощь
/order — сделать заказ

Пример:
/order Хочу заказать баннер
"""

            send_message(chat_id, answer)

        # =============================================
        # ORDER
        # =============================================

        elif text.startswith("/order"):

            order_text = text.replace("/order", "").strip()

            if order_text == "":
                send_message(
                    chat_id,
                    "Пример:\n/order Хочу заказать футболку"
                )

            else:
                send_message(
                    chat_id,
                    f"✅ Ваш заказ принят:\n\n{order_text}"
                )

        # =============================================
        # ОБЫЧНЫЕ СООБЩЕНИЯ
        # =============================================

        else:

            send_message(
                chat_id,
                f"Вы написали:\n\n{text}"
            )

        return jsonify({"status": "ok"})

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return jsonify({"status": "error"})


# =====================================================
# ЗАПУСК
# =====================================================


create_excel()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )