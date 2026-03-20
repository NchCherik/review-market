from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import sqlite3
import logging

# Настраиваем логи, чтобы видеть ошибки в панели Render
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Максимально разрешаем запросы с сайта

# --- ВСТАВЬ СВОИ ДАННЫЕ ТУТ ---
BOT_TOKEN = "8561764864:AAFoVwWzfQ4nyvwCzoa4JrUlt0s5pr_oDP0"
ADMIN_ID = "7062047050"

def get_db_connection():
    # Используем путь /tmp/, так как на Render это единственное место с правами записи
    conn = sqlite3.connect('/tmp/users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
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
        logging.info("База данных успешно инициализирована")
    except Exception as e:
        logging.error(f"Ошибка БД: {e}")

init_db()

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                       (username, email, password))
        conn.commit()
        conn.close()
        
        msg = f"🆕 Новый юзер: {username}\nEmail: {email}"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": ADMIN_ID, "text": msg})
        
        return jsonify({"status": "ok"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Логин занят"}), 400
    except Exception as e:
        logging.error(f"Ошибка регистрации: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/order', methods=['POST', 'OPTIONS'])
def handle_order():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        message = (
            f"🚀 НОВЫЙ ЗАКАЗ!\n\n"
            f"📍 Площадка: {data.get('type')}\n"
            f"📦 Объект: {data.get('target')}\n"
            f"🎯 Фокус: {data.get('focus')}\n"
            f"🔢 Кол-во: {data.get('quantity')}\n"
            f"🔗 Ссылка: {data.get('link')}\n"
            f"👤 Контакт: {data.get('contact')}"
        )
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        res = requests.post(url, json={"chat_id": ADMIN_ID, "text": message})
        
        if res.ok:
            return jsonify({"status": "ok"}), 200
        else:
            logging.error(f"ТГ ошибка: {res.text}")
            return jsonify({"status": "error"}), 400
            
    except Exception as e:
        logging.error(f"Ошибка заказа: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
