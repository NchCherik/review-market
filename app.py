import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8561764864:AAFoVwWzfQ4nyvwCzoa4JrUlt0s5pr_oDP0"
ADMINS = ["7062047050", "7069587561"]

def send_tg_message(text):
    for admin_id in ADMINS:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": admin_id, "text": text, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=5)
        except:
            pass
    return True

@app.route('/')
def home():
    return "ReviewMarket Backend: Online"

@app.route('/order', methods=['POST'])
def send_order():
    data = request.json
    order_text = (
        "🚀 **НОВЫЙ ЗАКАЗ!**\n\n"
        f"📍 **Тип:** {data.get('type')}\n"
        f"📦 **Объект:** {data.get('target')}\n"
        f"🎯 **Фокус:** {data.get('focus')}\n"
        f"🔢 **Кол-во:** {data.get('quantity')}\n"
        f"🔗 **Ссылка:** {data.get('link')}\n"
        f"👤 **Контакт:** {data.get('contact')}"
    )
    send_tg_message(order_text)
    return jsonify({"status": "success"}), 200

@app.route('/auth-google', methods=['POST'])
def auth_google():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    
    # Уведомление в Телеграм о новом входе
    msg = f"👤 **Вход через Google**\nИмя: {name}\nEmail: {email}"
    send_tg_message(msg)
    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
