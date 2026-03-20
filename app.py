import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ТВОИ НАСТРОЙКИ
TOKEN = "8561764864:AAFoVwWzfQ4nyvwCzoa4JrUlt0s5pr_oDP0"
# СПИСОК АДМИНОВ (Твой ID и ID друга)
ADMINS = ["7062047050", "7069587561"]

def send_tg_order(text):
    """Отправка заказа всем админам из списка"""
    success = True
    for admin_id in ADMINS:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": admin_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload)
            if not response.ok:
                success = False
                print(f"Ошибка отправки админу {admin_id}: {response.text}")
        except Exception as e:
            success = False
            print(f"Ошибка связи при отправке {admin_id}: {e}")
    return success

@app.route('/')
def home():
    return "ReviewMarket Server: Online. Admins: 2"

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
    
    if send_tg_order(order_text):
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Failed to send to all admins"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
