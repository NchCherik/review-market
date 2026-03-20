import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Чтобы сайт на GitHub мог слать запросы на Render

# Настройки бота (замени на свои, если они хранятся не в переменных окружения)
TOKEN = os.environ.get("TELEGRAM_TOKEN", "ТВОЙ_ТОКЕН_БОТА")
ADMIN_ID = os.environ.get("ADMIN_ID", "ТВОЙ_ЧАТ_ID")

def send_tg_message(text):
    """Вспомогательная функция для отправки сообщений в ТГ"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.ok
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False

@app.route('/')
def home():
    # ФИКС: Теперь здесь просто текст, бот НЕ будет спамить при каждом запуске
    return "ReviewMarket Server: Online"

@app.route('/order', methods=['POST'])
def send_order():
    data = request.json
    
    # Формируем красивый текст заказа
    order_text = (
        "🚀 **НОВЫЙ ЗАКАЗ!**\n\n"
        f"📍 **Тип:** {data.get('type')}\n"
        f"📦 **Объект:** {data.get('target')}\n"
        f"🎯 **Фокус:** {data.get('focus')}\n"
        f"🔢 **Кол-во:** {data.get('quantity')}\n"
        f"🔗 **Ссылка:** {data.get('link')}\n"
        f"👤 **Контакт:** {data.get('contact')}"
    )
    
    if send_tg_message(order_text):
        return jsonify({"status": "success", "message": "Order sent to TG"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to send to TG"}), 500

@app.route('/register', methods=['POST'])
def register():
    # Тут твоя логика регистрации (если она есть)
    # Для теста просто отвечаем успехом
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
