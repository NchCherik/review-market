from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import sqlite3

app = Flask(__name__)
CORS(app)

# --- НАСТРОЙКИ TELEGRAM ---
BOT_TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН_ОТ_BOTFATHER"
ADMIN_ID = "ВСТАВЬ_СЮДА_СВОЙ_ID"

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Создаем таблицу пользователей, если её нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT,
            balance INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Запускаем создание базы при старте
init_db()

# МАРШРУТ ДЛЯ РЕГИСТРАЦИИ
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Заполните все поля"}), 400

    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                       (username, email, password))
        conn.commit()
        conn.close()
        
        # Уведомление тебе в ТГ о новом юзере
        msg = f"🆕 **Новый пользователь!**\nЛогин: {username}\nEmail: {email}"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": ADMIN_ID, "text": msg, "parse_mode": "Markdown"})
        
        return jsonify({"status": "ok"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Этот логин уже занят"}), 400

# МАРШРУТ ДЛЯ ЗАКАЗОВ (старый, рабочий)
@app.route('/order', methods=['POST'])
def handle_order():
    try:
        data = request.json
        message = (
            f"🚀 **НОВЫЙ ЗАКАЗ!**\n\n"
            f"📍 Площадка: {data.get('type')}\n"
            f"📦 Объект: {data.get('target')}\n"
            f"🎯 Фокус: {data.get('focus')}\n"
            f"🔢 Кол-во: {data.get('quantity')}\n"
            f"🔗 Ссылка: {data.get('link')}\n"
            f"👤 Контакт: {data.get('contact')}"
        )
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": ADMIN_ID, "text": message, "parse_mode": "Markdown"})
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
