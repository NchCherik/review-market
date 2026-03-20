from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app) # Разрешаем сайту подключаться к серверу

# ВСТАВЬ СВОИ ДАННЫЕ ТУТ (клиент их никогда не увидит)
BOT_TOKEN = "8561764864:AAFoVwWzfQ4nyvwCzoa4JrUlt0s5pr_oDP0"
ADMIN_ID = "7062047050"

@app.route('/order', methods=['POST'])
def handle_order():
    data = request.json
    
    # Собираем красивое сообщение
    message = (
        f"🔔 **НОВЫЙ ЗАКАЗ!**\n\n"
        f"📍 Площадка: {data.get('type')}\n"
        f"📦 Куда: {data.get('target')}\n"
        f"🎯 Фокус: {data.get('focus')}\n"
        f"🔢 Кол-во: {data.get('quantity')}\n"
        f"🔗 Ссылка: {data.get('link')}\n"
        f"👤 Контакт: {data.get('contact')}"
    )

    # Отправляем в Telegram
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={"chat_id": ADMIN_ID, "text": message, "parse_mode": "Markdown"})
    
    if res.ok:
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(port=5000)