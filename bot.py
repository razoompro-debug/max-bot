from flask import Flask, request, jsonify
import requests
import os
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
            print("✅ EXCEL CREATED")
    except Exception as e:
        print("❌ CREATE EXCEL ERROR:", e)

# =====================================================
# СОХРАНЕНИЕ СООБЩЕНИЯ В EXCEL
# =====================================================

def save_to_excel(user_id, name, text):
    try:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws.append([date_str, user_id, name, text])
        wb.save(EXCEL_FILE)
    except Exception as e:
        print("❌ ERROR SAVING TO EXCEL:", e)

# =====================================================
# ОТПРАВКА СООБЩЕНИЯ
# =====================================================

def send_message(chat_id, text):
    # Предполагается стандартная структура API для MAX, похожая на Telegram
    # Если MAX использует другой эндпоинт, скорректируйте URL (например, /messages/sendText)
    url = f"{API_URL}/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR SENDING MESSAGE to {chat_id}:", e)

# =====================================================
# ОБРАБОТКА ВЕБХУКОВ
# =====================================================

@app.route("/", methods=["POST", "GET"])
def webhook():
    # Игнорируем GET-запросы (например, при проверке доступности сервера)
    if request.method == "GET":
        return "Бот работает!", 200

    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload"}), 400

        # Парсинг данных (структура может немного отличаться в зависимости от API MAX)
        # Здесь приведена стандартная структура Telegram-подобных API
        message = data.get("message", {})
        chat = message.get("chat", {})
        user = message.get("from", {})
        
        chat_id = chat.get("id")
        text = message.get("text", "").strip()
        user_id = user.get("id", "Unknown")
        first_name = user.get("first_name", "User")

        if not chat_id or not text:
            return jsonify({"status": "ok", "message": "Ignored"}), 200

        # Сохраняем каждый запрос в базу (Excel)
        save_to_excel(user_id, first_name, text)

        # =============================================
        # START
        # =============================================
        if text == "/start":
            answer = "Привет! Я бот.\nВведите /help для списка команд."
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
        print("❌ WEBHOOK ERROR:", e)
        return jsonify({"status": "error"}), 500

# =====================================================
# ЗАПУСК
# =====================================================

if __name__ == "__main__":
    create_excel()
    # Запускаем Flask-сервер (по умолчанию порт 5000)
    # Для production рекомендуется использовать Gunicorn или Waitress
    app.run(host="0.0.0.0", port=5000, debug=False)