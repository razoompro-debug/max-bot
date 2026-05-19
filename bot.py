from flask import Flask, request, jsonify
import requests
import os
import time
from openpyxl import Workbook, load_workbook
from datetime import datetime

# ==================================================
# НАСТРОЙКИ
# ==================================================

TOKEN = "f9LHodD0cOIloCdM4S4u2QEo0hF1yDOLdVH23RWt5jZwWyIWM82UMhtRYvdd5vPJJ4jYfNEjdPrbnSAV4siW"

API_URL = "https://botapi.max.ru"

ADMIN_CHAT_ID = 290993557

EXCEL_FILE = "orders.xlsx"

app = Flask(__name__)

# ==================================================
# СОЗДАНИЕ EXCEL
# ==================================================


def create_excel():
    try:
        if not os.path.exists(EXCEL_FILE):
            wb = Workbook()
            ws = wb.active

            ws.title = "Orders"

            ws.append([
                "Дата",
                "Chat ID",
                "Имя",
                "Сообщение"
            ])

            wb.save(EXCEL_FILE)

            print("EXCEL CREATED")

    except Exception as e:
        print("EXCEL CREATE ERROR:", str(e))


# ==================================================
# СОХРАНЕНИЕ СООБЩЕНИЯ
# ==================================================


def save_message(chat_id, user_name, text):
    try:
        create_excel()

        wb = load_workbook(EXCEL_FILE)
        ws = wb.active

        ws.append([
            datetime.now().strftime("%d.%m.%Y %H:%M"),
            str(chat_id),
            user_name,
            text
        ])

        wb.save(EXCEL_FILE)

        print("MESSAGE SAVED")

    except Exception as e:
        print("SAVE ERROR:", str(e))


# ==================================================
# ОТПРАВКА СООБЩЕНИЯ
# ==================================================


def send_message(chat_id, text):
    try:
        print("================================")
        print("SEND MESSAGE")
        print("CHAT:", chat_id)

        time.sleep(1)

        url = f"{API_URL}/message/send"

        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "chat_id": int(chat_id),
            "text": text
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=15
        )

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        # защита от лимитов
        if response.status_code == 429:
            print("RATE LIMIT -> WAIT")
            time.sleep(3)

        print("================================")

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
    try:
        data = request.json

        print("WEBHOOK DATA:", data)

        # --------------------------------------------------
        # BOT STARTED EVENT
        # --------------------------------------------------

        if data.get("update_type") == "bot_started":
            print("BOT STARTED EVENT")

            return jsonify({
                "status": "ok"
            })

        # --------------------------------------------------
        # MESSAGE
        # --------------------------------------------------

        message = data.get("message")

        if not message:
            print("NO MESSAGE")

            return jsonify({
                "status": "no_message"
            })

        body = message.get("body", {})
        sender = message.get("sender", {})
        recipient = message.get("recipient", {})

        text = body.get("text", "").strip()

        chat_id = recipient.get("chat_id")

        user_name = sender.get(
            "first_name",
            "Пользователь"
        )

        print("CHAT ID:", chat_id)
        print("TEXT:", text)

        # --------------------------------------------------
        # ПРОВЕРКА
        # --------------------------------------------------

        if not chat_id:
            print("NO CHAT ID")

            return jsonify({
                "status": "no_chat_id"
            })

        if not text:
            print("EMPTY TEXT")

            return jsonify({
                "status": "empty_text"
            })

        # --------------------------------------------------
        # СОХРАНЯЕМ СООБЩЕНИЕ
        # --------------------------------------------------

        save_message(
            chat_id,
            user_name,
            text
        )

        # --------------------------------------------------
        # /start
        # --------------------------------------------------

        if text == "/start":

            answer = f"""
👋 Здравствуйте, {user_name}!

Добро пожаловать в MAX бот.

Доступные команды:

/start — запуск
/help — помощь
/order — оформить заказ

Пример:

/order Хочу заказать футболку
"""

            send_message(chat_id, answer)

        # --------------------------------------------------
        # /help
        # --------------------------------------------------

        elif text == "/help":

            send_message(
                chat_id,
                """
Команды:

/start
/help
/order

Пример заказа:

/order Хочу заказать футболку
"""
            )

        # --------------------------------------------------
        # /order
        # --------------------------------------------------

        elif text.startswith("/order"):

            order_text = text.replace(
                "/order",
                ""
            ).strip()

            if order_text == "":

                send_message(
                    chat_id,
                    """
Пример:

/order Хочу заказать футболку
"""
                )

            else:

                # сообщение пользователю
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

        # --------------------------------------------------
        # ОБЫЧНОЕ СООБЩЕНИЕ
        # --------------------------------------------------

        else:

            send_message(
                chat_id,
                f"Вы написали: {text}"
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


# ==================================================
# ЗАПУСК
# ==================================================


create_excel()


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
