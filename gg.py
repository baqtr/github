import os
import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
import requests
from dotenv import load_dotenv

load_dotenv()

bot_token = "7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20"  # توكن البوت في تليجرام
bot = telebot.TeleBot(API_TOKEN)

user_data = {}
safe_mode = {}

HEROKU_BASE_URL = 'https://api.heroku.com'

# وظيفة بدء التشغيل
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    add_api_button = types.InlineKeyboardButton("إضافة API", callback_data="add_api")
    my_accounts_button = types.InlineKeyboardButton("حساباتك", callback_data="my_accounts")
    safe_mode_button = types.InlineKeyboardButton(f"الوضع الآمن: {'مفعل ✅' if safe_mode.get(message.chat.id, False) else 'معطل ❌'}", callback_data="toggle_safe_mode")
    markup.add(add_api_button, my_accounts_button, safe_mode_button)
    bot.send_message(message.chat.id, "مرحبًا بك! اختر أحد الخيارات:", reply_markup=markup)

# وظيفة إضافة API
@bot.callback_query_handler(func=lambda call: call.data == "add_api")
def add_api(call):
    msg = bot.send_message(call.message.chat.id, "أرسل لي API الخاص بك:")
    bot.register_next_step_handler(msg, save_api)

def save_api(message):
    user_id = message.chat.id
    api_key = message.text
    if user_id not in user_data:
        user_data[user_id] = []
    user_data[user_id].append(api_key)
    bot.send_message(message.chat.id, "تم حفظ API بنجاح.")

# عرض الحسابات
@bot.callback_query_handler(func=lambda call: call.data == "my_accounts")
def my_accounts(call):
    user_id = call.message.chat.id
    if user_id not in user_data or not user_data[user_id]:
        bot.send_message(user_id, "لا توجد حسابات مضافة.")
        return

    markup = types.InlineKeyboardMarkup()
    for index, api_key in enumerate(user_data[user_id]):
        account_button = types.InlineKeyboardButton(f"حساب {index+1}", callback_data=f"account_{index}")
        markup.add(account_button)
    back_button = types.InlineKeyboardButton("الرجوع", callback_data="go_back")
    markup.add(back_button)
    bot.send_message(user_id, "اختر حسابًا:", reply_markup=markup)

# وظيفة التحكم في الحساب
@bot.callback_query_handler(func=lambda call: call.data.startswith("account_"))
def account_control(call):
    user_id = call.message.chat.id
    account_index = int(call.data.split("_")[1])
    if user_id not in user_data or account_index >= len(user_data[user_id]):
        bot.send_message(user_id, "حساب غير صالح.")
        return

    api_key = user_data[user_id][account_index]
    markup = types.InlineKeyboardMarkup()
    create_app_button = types.InlineKeyboardButton("إنشاء تطبيق", callback_data=f"create_app_{account_index}")
    delete_app_button = types.InlineKeyboardButton("حذف تطبيق", callback_data=f"delete_app_{account_index}")
    back_button = types.InlineKeyboardButton("الرجوع", callback_data="my_accounts")
    markup.add(create_app_button, delete_app_button, back_button)
    bot.send_message(user_id, "اختر إجراء:", reply_markup=markup)

# وظيفة إنشاء تطبيق
@bot.callback_query_handler(func=lambda call: call.data.startswith("create_app_"))
def create_app(call):
    account_index = int(call.data.split("_")[2])
    msg = bot.send_message(call.message.chat.id, "أدخل اسم التطبيق:")
    bot.register_next_step_handler(msg, lambda m: handle_create_app(m, account_index))

def handle_create_app(message, account_index):
    user_id = message.chat.id
    app_name = message.text
    api_key = user_data[user_id][account_index]

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3',
        'Content-Type': 'application/json'
    }
    data = {
        'name': app_name
    }
    response = requests.post(f'{HEROKU_BASE_URL}/apps', headers=headers, json=data)
    if response.status_code == 201:
        bot.send_message(user_id, "تم إنشاء التطبيق بنجاح.")
    else:
        bot.send_message(user_id, "فشل في إنشاء التطبيق.")

# وظيفة حذف تطبيق
@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_app_"))
def delete_app(call):
    account_index = int(call.data.split("_")[2])
    msg = bot.send_message(call.message.chat.id, "أدخل اسم التطبيق الذي تريد حذفه:")
    bot.register_next_step_handler(msg, lambda m: handle_delete_app(m, account_index))

def handle_delete_app(message, account_index):
    user_id = message.chat.id
    app_name = message.text
    if safe_mode.get(user_id, False):
        bot.send_message(user_id, "لا يمكن حذف التطبيق بسبب تفعيل الوضع الآمن.")
        return

    api_key = user_data[user_id][account_index]
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    response = requests.delete(f'{HEROKU_BASE_URL}/apps/{app_name}', headers=headers)
    if response.status_code == 202:
        bot.send_message(user_id, "تم حذف التطبيق بنجاح.")
    else:
        bot.send_message(user_id, "فشل في حذف التطبيق.")

# وظيفة تفعيل وتعطيل الوضع الآمن
@bot.callback_query_handler(func=lambda call: call.data == "toggle_safe_mode")
def toggle_safe_mode(call):
    user_id = call.message.chat.id
    safe_mode[user_id] = not safe_mode.get(user_id, False)
    status = 'مفعل ✅' if safe_mode[user_id] else 'معطل ❌'
    bot.send_message(user_id, f"تم تغيير وضع الآمن إلى: {status}")
    start(call.message)

# وظيفة الرجوع
@bot.callback_query_handler(func=lambda call: call.data == "go_back")
def go_back(call):
    start(call.message)

# بدء تشغيل البوت
bot.polling()
