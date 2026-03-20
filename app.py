import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с GitHub Pages

# ТВОИ ОБНОВЛЕННЫЕ ДАННЫЕ
TOKEN = "8561764864:AAFoVwWzfQ4nyvwCzoa4JrUlt0s5pr_oDP0"
ADMIN_ID = "7062047050"

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
    # ФИКС: Просто текстовый ответ, чтобы бот не спамил в личку
    return "ReviewMarket Server: Online and Ready!"

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
    # Ответ для страницы регистрации (пока просто успех)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Автоматический выбор порта для Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
