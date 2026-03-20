import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с GitHub Pages

# ТВОИ ДАННЫЕ ИЗ ПРЕДЫДУЩИХ СООБЩЕНИЙ
TOKEN = "7547690186:AAEn_T-Y47-rT-qP47v5_Xo3vXo3vXo3vXo" # Твой токен бота
ADMIN_ID = "1214154425" # Твой Telegram ID

def send_tg_message(text):
    """Отправка сообщения в Telegram"""
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
    # ФИКС: Убрали спам при запуске. Теперь сервер просто отвечает текстом.
    return "ReviewMarket Server: Online and Ready!"

@app.route('/order', methods=['POST'])
def send_order():
    data = request.json
    
    # Формируем красивый текст заказа, как на твоем скриншоте
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
    # Ответ для страницы регистрации
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Настройка порта для Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
