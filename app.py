import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

# =========================================================
# ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ
# =========================================================
app = Flask(__name__)
CORS(app)

# --- ЧТЕНИЕ НАСТРОЕК ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ---
# Эти данные теперь берутся из настроек Render, а не из кода
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# Подключение к базе данных
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# 1. ПОЛУЧЕНИЕ БАЛАНСА И АВТО-РЕГИСТРАЦИЯ
# =========================================================
@app.route('/get_balance', methods=['POST'])
def get_balance():
    try:
        data = request.json
        email = data.get('email')
        user_name = data.get('name', 'Користувач')

        if not email:
            return jsonify({"error": "Email is required"}), 400

        user_query = supabase.table("profiles").select("*").eq("email", email).execute()
        
        if not user_query.data:
            supabase.table("profiles").insert({
                "email": email, 
                "name": user_name, 
                "balance": 0.0
            }).execute()
            return jsonify({"balance": 0.0})
        
        return jsonify({"balance": user_query.data[0]['balance']})

    except Exception as e:
        print(f"Помилка при отриманні балансу: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# =========================================================
# 2. ИСПРАВЛЕННАЯ СИСТЕМА АДМИН-ПОПОЛНЕНИЯ
# =========================================================
@app.route('/admin/topup', methods=['POST'])
def admin_topup():
    try:
        data = request.json
        provided_password = str(data.get('password'))
        target_email = data.get('email')
        
        try:
            amount_to_add = float(data.get('amount', 0))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Некоректна сума"}), 400

        # Сравниваем с паролем из переменных окружения
        if provided_password != str(ADMIN_PASSWORD):
            return jsonify({"success": False, "error": "Доступ заборонено: невірний пароль"}), 403

        user_data = supabase.table("profiles").select("balance").eq("email", target_email).execute()
        
        if user_data.data:
            current_balance = float(user_data.data[0]['balance'])
            new_balance = current_balance + amount_to_add
            
            supabase.table("profiles").update({"balance": new_balance}).eq("email", target_email).execute()
            
            admin_log = (
                f"🛠 **АДМІН-ПОПОВНЕННЯ**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📧 Email: {target_email}\n"
                f"💰 Додано: +{amount_to_add} ₴\n"
                f"💎 Новий баланс: {new_balance} ₴"
            )
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                          json={"chat_id": TELEGRAM_CHAT_ID, "text": admin_log, "parse_mode": "Markdown"})
            
            return jsonify({"success": True, "new_balance": new_balance})
        else:
            return jsonify({"success": False, "error": "Користувача не знайдено в базі"}), 404

    except Exception as e:
        print(f"Критична помилка адмінки: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =========================================================
# 3. ОБРАБОТКА ЗАКАЗА СО СПИСАНИЕМ СРЕДСТВ
# =========================================================
@app.route('/order', methods=['POST'])
def handle_order():
    try:
        data = request.json
        email = data.get('user_email')
        
        try:
            price = float(data.get('price', 0))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Помилка вартості"}), 400

        order_type = data.get('type', 'Не вказано')
        package_name = data.get('package', 'Стандарт')
        target_link = data.get('target', 'Не вказано')
        contact_info = data.get('contact', 'Не вказано')
        additional_info = data.get('details', 'Немає')

        user_check = supabase.table("profiles").select("balance").eq("email", email).execute()
        
        if not user_check.data:
            return jsonify({"success": False, "error": "Користувача не знайдено"}), 404
            
        current_user_balance = float(user_check.data[0]['balance'])
        
        if current_user_balance < price:
            return jsonify({"success": False, "error": "Недостатньо коштів на балансі!"}), 400

        new_balance = current_user_balance - price
        supabase.table("profiles").update({"balance": new_balance}).eq("email", email).execute()

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
            f"💎 **Залишок на балансі:** {new_balance} ₴"
        )
        
        tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(tg_url, json={
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": tg_message, 
            "parse_mode": "Markdown"
        })

        return jsonify({"success": True, "new_balance": new_balance})

    except Exception as e:
        print(f"Помилка при оформленні замовлення: {e}")
        return jsonify({"success": False, "error": "Помилка сервера"}), 500

# =========================================================
# ЗАПУСК СЕРВЕРА
# =========================================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
