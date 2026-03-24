import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# --- НАСТРОЙКИ (ВСТАВЬ СВОИ ДАННЫЕ) ---
SUPABASE_URL = "https://muunhaompmqkariozjjv.supabase.co"
SUPABASE_KEY = "sb_publishable_3pTVyZK26luZUch_HdkAJQ_ABFHDxr5"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_TOKEN = "8561764864:AAFoVwWzfQ4nyvwCzoa4JrUlt0s5pr_oDP0"
TELEGRAM_CHAT_ID = "7062047050"
ADMIN_PASSWORD = "Lololowka" 

# 1. ПОЛУЧЕНИЕ БАЛАНСА
@app.route('/get_balance', methods=['POST'])
def get_balance():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name', 'Користувач')
        if not email:
            return jsonify({"error": "Email is required"}), 400
        user_query = supabase.table("profiles").select("*").eq("email", email).execute()
        if not user_query.data:
            supabase.table("profiles").insert({"email": email, "name": name, "balance": 0}).execute()
            return jsonify({"balance": 0})
        return jsonify({"balance": user_query.data[0]['balance']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. АДМИН-ПОПОЛНЕНИЕ (СЕКРЕТНАЯ КНОПКА)
@app.route('/admin/topup', methods=['POST'])
def admin_topup():
    data = request.json
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({"success": False, "error": "Невірний пароль"}), 403
    email = data.get('email')
    amount = int(data.get('amount'))
    try:
        user_query = supabase.table("profiles").select("balance").eq("email", email).execute()
        if user_query.data:
            new_balance = user_query.data[0]['balance'] + amount
            supabase.table("profiles").update({"balance": new_balance}).eq("email", email).execute()
            return jsonify({"success": True, "new_balance": new_balance})
        return jsonify({"success": False, "error": "Користувача не знайдено"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 3. ОБРАБОТКА ЗАКАЗА (ДИНАМИЧЕСКАЯ ЦЕНА)
@app.route('/order', methods=['POST'])
def handle_order():
    try:
        data = request.json
        email = data.get('user_email')
        price = int(data.get('price', 50)) 
        user_check = supabase.table("profiles").select("balance").eq("email", email).execute()
        if not user_check.data or user_check.data[0]['balance'] < price:
            return jsonify({"success": False, "error": "Недостатньо коштів!"}), 400
        new_balance = user_check.data[0]['balance'] - price
        supabase.table("profiles").update({"balance": new_balance}).eq("email", email).execute()
        
        # Текст для Telegram
        text = (
            f"💰 **НОВЕ ЗАМОВЛЕННЯ**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📧 Email: {email}\n"
            f"📦 Пакет: {data.get('package')}\n"
            f"📋 Тип: {data.get('type')}\n"
            f"📍 Ціль: {data.get('target')}\n"
            f"👤 Контакт: {data.get('contact')}\n"
            f"📝 Деталі: {data.get('details', 'Не вказано')}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"✅ Списано: {price} ₴\n"
            f"💎 Залишок: {new_balance} ₴"
        )
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"})
        return jsonify({"success": True, "new_balance": new_balance})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
