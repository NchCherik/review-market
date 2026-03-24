import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

# --- ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ ---
app = Flask(__name__)
CORS(app)

# --- НАСТРОЙКИ БАЗЫ ДАННЫХ SUPABASE ---
# Твой URL проекта
SUPABASE_URL = "https://muunhaompmqkariozjjv.supabase.co"
# Твой ANON KEY (длинная строка со скриншота)
SUPABASE_KEY = "sb_publishable_3pTVyZK26luZUch_HdkAJQ_ABFHDxr5"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- НАСТРОЙКИ УВЕДОМЛЕНИЙ TELEGRAM ---
TELEGRAM_TOKEN = "8561764864:AAFoVwWzfQ4nyvwCzoa4JrUlt0s5pr_oDP0"
TELEGRAM_CHAT_ID = "7062047050"

# ПАРОЛЬ ДЛЯ СЕКРЕТНОГО ПОПОЛНЕНИЯ (ИЗМЕНИ НА СВОЙ)
ADMIN_PASSWORD = "ГОРЯЧИЙ_ПАРОЛЬ_123"

# ---------------------------------------------------------
# 1. МАРШРУТ: ПОЛУЧЕНИЕ БАЛАНСА И АВТО-РЕГИСТРАЦИЯ
# ---------------------------------------------------------
@app.route('/get_balance', methods=['POST'])
def get_balance():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name', 'Користувач')

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Поиск пользователя в таблице profiles
        user_query = supabase.table("profiles").select("*").eq("email", email).execute()
        
        if not user_query.data:
            # Если пользователя нет — регистрируем его с балансом 0
            supabase.table("profiles").insert({
                "email": email, 
                "name": name, 
                "balance": 0
            }).execute()
            return jsonify({"balance": 0})
        
        # Если есть — отдаем его баланс
        return jsonify({"balance": user_query.data[0]['balance']})

    except Exception as e:
        print(f"Ошибка получения баланса: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# ---------------------------------------------------------
# 2. МАРШРУТ: СЕКРЕТНОЕ ПОПОЛНЕНИЕ (АДМИН-ПАНЕЛЬ)
# ---------------------------------------------------------
@app.route('/admin/topup', methods=['POST'])
def admin_topup():
    try:
        data = request.json
        provided_password = data.get('password')
        target_email = data.get('email')
        amount_to_add = int(data.get('amount', 0))

        # Проверка прав доступа
        if provided_password != ADMIN_PASSWORD:
            return jsonify({"success": False, "error": "Доступ заборонено!"}), 403

        # Проверка наличия пользователя
        check_user = supabase.table("profiles").select("balance").eq("email", target_email).execute()
        
        if check_user.data:
            current_bal = check_user.data[0]['balance']
            new_bal = current_bal + amount_to_add
            
            # Обновление баланса в базе
            supabase.table("profiles").update({"balance": new_bal}).eq("email", target_email).execute()
            
            return jsonify({"success": True, "new_balance": new_bal})
        else:
            return jsonify({"success": False, "error": "Користувач не знайдений"}), 404

    except Exception as e:
        print(f"Ошибка админки: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------------------------------------------------
# 3. МАРШРУТ: ОБРАБОТКА ЗАКАЗА СО СПИСАНИЕМ
# ---------------------------------------------------------
@app.route('/order', methods=['POST'])
def handle_order():
    try:
        data = request.json
        email = data.get('user_email')
        price = int(data.get('price', 0)) # Цена теперь приходит с сайта
        order_type = data.get('type', 'Не вказано')
        package_name = data.get('package', 'Стандарт')
        target_link = data.get('target', 'Не вказано')
        contact_info = data.get('contact', 'Не вказано')
        additional_info = data.get('details', 'Немає')

        # Проверяем, хватает ли денег
        user_check = supabase.table("profiles").select("balance").eq("email", email).execute()
        
        if not user_check.data or user_check.data[0]['balance'] < price:
            return jsonify({"success": False, "error": "Недостатньо коштів на балансі!"}), 400

        # Списание средств
        new_balance = user_check.data[0]['balance'] - price
        supabase.table("profiles").update({"balance": new_balance}).eq("email", email).execute()

        # Формирование сообщения для Telegram
        tg_message = (
            f"🚀 **НОВЕ ЗАМОВЛЕННЯ: {order_type}**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📧 **Клієнт:** {email}\n"
            f"📦 **Пакет:** {package_name}\n"
            f"📍 **Ціль:** {target_link}\n"
            f"👤 **Контакт:** {contact_info}\n"
            f"📝 **Деталі:** {additional_info}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ **Списано:** {price} ₴\n"
            f"💎 **Залишок:** {new_balance} ₴"
        )
        
        # Отправка в бота
        tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(tg_url, json={
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": tg_message, 
            "parse_mode": "Markdown"
        })

        return jsonify({"success": True, "new_balance": new_balance})

    except Exception as e:
        print(f"Ошибка заказа: {e}")
        return jsonify({"success": False, "error": "Помилка сервера"}), 500

# --- ЗАПУСК ---
if __name__ == '__main__':
    # Порт для Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
