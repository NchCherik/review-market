from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import sqlite3

app = Flask(__name__)
# Разрешаем запросы со всех адресов, чтобы сайт мог достучаться до сервера
CORS(app, resources={r"/*": {"origins": "*"}})

# --- ТВОИ ДАННЫЕ УЖЕ ТУТ ---
BOT_TOKEN = "8561764864:AAFoVwWzfQ4nyvwCzoa4JrUlt0s5pr_oDP0"
ADMIN_ID = "7062047050"

# Функция для отправки сообщений в ТГ
def send_tg_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        res = requests.post(url, json={"chat_id": ADMIN_ID, "text": text, "parse_mode": "Markdown"})
        return res.ok
    except:
        return False

# 1. Проверка работы сервера (просто открой ссылку https://review-market.onrender.com/)
@app.route('/')
def home():
    if send_tg_message("✅ **ReviewMarket:** Сервер успешно запущен и видит твой ID!"):
        return "Бот работает! Проверь Телеграм."
    return "Ошибка! Проверь, нажал ли ты START в боте."

# 2. Регистрация нового пользователя
@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    try:
        # Используем /tmp/ для базы данных на Render
        conn = sqlite3.connect('/tmp/users.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, email TEXT, password TEXT)')
        cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
        conn.close()

        send_tg_message(f"🆕 **Новый пользователь!**\nЛогин: `{username}`\nEmail: `{email}`")
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. Прием заказов
@app.route('/order', methods=['POST', 'OPTIONS'])
def handle_order():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.json
    message = (
        f"🚀 **НОВЫЙ ЗАКАЗ!**\n\n"
        f"📍 Тип: {data.get('type')}\n"
        f"📦 Объект: {data.get('target')}\n"
        f"🎯 Фокус: {data.get('focus')}\n"
        f"🔢 Кол-во: {data.get('quantity')}\n"
        f"🔗 Ссылка: {data.get('link')}\n"
        f"👤 Контакт: {data.get('contact')}"
    )
    
    if send_tg_message(message):
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
