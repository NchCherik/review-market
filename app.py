import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# --- НАСТРОЙКИ SUPABASE ---
# Твой ID проекта уже вшит в URL
SUPABASE_URL = "https://muunhaompmqkariozjjv.supabase.co"
# Вставь сюда длинный ключ (anon public) со своего скриншота
SUPABASE_KEY = "sb_publishable_3pTVyZK26luZUch_HdkAJQ_ABFHDxr5"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- НАСТРОЙКИ TELEGRAM ---
TELEGRAM_TOKEN = "8561764864:AAFoVwWzfQ4nyvwCzoa4JrUlt0s5pr_oDP0"
TELEGRAM_CHAT_ID = "7062047050"

# 1. ПОЛУЧЕНИЕ БАЛАНСА И АВТО-РЕГИСТРАЦИЯ
@app.route('/get_balance', methods=['POST'])
def get_balance():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name', 'Пользователь')

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Проверяем, есть ли такой email в таблице profiles
        user_query = supabase.table("profiles").select("*").eq("email", email).execute()
        
        if not user_query.data:
            # Если юзера нет — создаем новую запись с балансом 0
            supabase.table("profiles").insert({
                "email": email, 
                "name": name, 
                "balance": 0
            }).execute()
            return jsonify({"balance": 0})
        
        # Если юзер есть — возвращаем его текущий баланс
        return jsonify({"balance": user_query.data[0]['balance']})
    except Exception as e:
        print(f"Ошибка базы данных: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# 2. ОБРАБОТКА ЗАКАЗА СО СПИСАНИЕМ
@app.route('/order', methods=['POST'])
def handle_order():
    try:
        data = request.json
        email = data.get('user_email')
        # Давай поставим цену, например, 50 ₽ за заказ
        PRICE = 50 

        # Проверяем текущий баланс юзера
        user_check = supabase.table("profiles").select("balance").eq("email", email).execute()
        
        if not user_check.data or user_check.data[0]['balance'] < PRICE:
            return jsonify({"success": False, "error": "Недостаточно средств!"}), 400

        # Списываем баланс
        current_balance = user_check.data[0]['balance']
        new_balance = current_balance - PRICE
        supabase.table("profiles").update({"balance": new_balance}).eq("email", email).execute()

        # Отправляем уведомление в Telegram
        text = (
            f"💰 **СПИСАНИЕ И ЗАКАЗ**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📧 Email: {email}\n"
            f"📋 Тип: {data.get('type')}\n"
            f"📍 Ссылка/Цель: {data.get('target')}\n"
            f"🔢 Кол-во: {data.get('quantity')}\n"
            f"👤 Контакт: {data.get('contact')}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"✅ Списано: {PRICE} ₽\n"
            f"💎 Остаток: {new_balance} ₽"
        )
        
        tg_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(tg_api, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"})

        return jsonify({"success": True, "new_balance": new_balance})

    except Exception as e:
        print(f"Ошибка заказа: {e}")
        return jsonify({"success": False, "error": "Server error"}), 500

if __name__ == '__main__':
    # На Render порт берется из переменной окружения
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
