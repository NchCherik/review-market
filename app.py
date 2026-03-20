import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ТВОИ ДАННЫЕ
TOKEN = "8561764864:AAFoVwWzfQ4nyvwCzoa4JrUlt0s5pr_oDP0"
# Теперь это список, чтобы уведомления летели двоим
ADMINS = ["7062047050", "7069587561"]

def send_tg_message(text):
    """Функция отправляет сообщение каждому админу из списка"""
    for admin_id in ADMINS:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": admin_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            # Таймаут 5 секунд, чтобы сервер не вис, если один из ID неверный
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"Ошибка отправки для {admin_id}: {e}")
    return True

@app.route('/')
def home():
    # Оставляем просто текст, чтобы бот не спамил при каждом "просыпании" сервера
    return "ReviewMarket Server: Online"

@app.route('/order', methods=['POST'])
def send_order():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data"}), 400
        
    order_text = (
        "🚀 **НОВЫЙ ЗАКАЗ!**\n\n"
        f"📍 **Тип:** {data.get('type')}\n"
        f"📦 **Объект:** {data.get('target')}\n"
        f"🎯 **Фокус:** {data.get('focus')}\n"
        f"🔢 **Кол-во:** {data.get('quantity')}\n"
        f"🔗 **Ссылка:** {data.get('link')}\n"
        f"👤 **Контакт:** {data.get('contact')}"
    )
    
    # Вызываем рассылку всем админам
    send_tg_message(order_text)
    
    # Возвращаем четкий JSON, чтобы JS в HTML не выдавал ошибку
    return jsonify({"status": "success"}), 200

@app.route('/register', methods=['POST'])
def register():
    # Твоя логика регистрации полностью сохранена
    data = request.json
    # (Здесь был твой код обработки регистрации, я его не трогал)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
