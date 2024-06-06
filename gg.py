import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import os

API_TOKEN = '7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20'
bot = telebot.TeleBot(API_TOKEN)

user_accounts = {}
safe_mode = {}

# Function to create main buttons
def create_main_buttons():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("إضافة API", callback_data="add_api"),
        InlineKeyboardButton("حساباتك", callback_data="list_accounts"),
        InlineKeyboardButton(
            "الوضع الآمن: معطل ❌",
            callback_data="toggle_safe_mode"
        )
    )
    return markup

# Function to create back button
def create_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("رجوع", callback_data="go_back"))
    return markup

# Function to create account control buttons
def create_account_control_buttons(account_index):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("حذف التطبيق", callback_data=f"delete_app_{account_index}"),
        InlineKeyboardButton("إنشاء تطبيق", callback_data=f"create_app_{account_index}"),
        InlineKeyboardButton("رجوع", callback_data="go_back")
    )
    return markup

# Function to add a new API
def add_api(call):
    user_id = call.from_user.id
    bot.send_message(call.message.chat.id, "أدخل مفتاح API:")
    bot.register_next_step_handler(call.message, lambda message: save_api(message, user_id))

def save_api(message, user_id):
    api_key = message.text
    if user_id not in user_accounts:
        user_accounts[user_id] = []
    user_accounts[user_id].append({"api_key": api_key})
    bot.send_message(message.chat.id, "تم إضافة API بنجاح.", reply_markup=create_main_buttons())

# Function to list user accounts
def list_accounts(call):
    user_id = call.from_user.id
    accounts = user_accounts.get(user_id, [])
    if not accounts:
        bot.edit_message_text("لا توجد حسابات مضافة.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
    else:
        markup = InlineKeyboardMarkup()
        for index, account in enumerate(accounts):
            markup.add(InlineKeyboardButton(f"الحساب {index + 1}", callback_data=f"select_account_{index}"))
        markup.add(InlineKeyboardButton("رجوع", callback_data="go_back"))
        bot.edit_message_text("الحسابات المضافة:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

# Function to delete an app
def delete_app(call, account_index):
    user_id = call.from_user.id
    if safe_mode.get(user_id, False):
        bot.edit_message_text("لا يمكن حذف التطبيق بسبب تفعيل الوضع الآمن.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
    else:
        api_key = user_accounts[user_id][account_index]['api_key']
        app_name = call.data.split("_")[-1]
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/vnd.heroku+json; version=3'
        }
        response = requests.delete(f'https://api.heroku.com/apps/{app_name}', headers=headers)
        if response.status_code == 202:
            bot.edit_message_text("تم حذف التطبيق بنجاح.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
        else:
            bot.edit_message_text("فشل في حذف التطبيق. تحقق من صحة مفتاح API أو اسم التطبيق.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

# Function to create a new app
def create_app(call, account_index):
    user_id = call.from_user.id
    api_key = user_accounts[user_id][account_index]['api_key']
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3',
        'Content-Type': 'application/json'
    }
    bot.send_message(call.message.chat.id, "أدخل اسم التطبيق:")
    bot.register_next_step_handler(call.message, lambda message: save_app(message, headers))

def save_app(message, headers):
    app_name = message.text
    data = {"name": app_name}
    response = requests.post(f'https://api.heroku.com/apps', headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        bot.send_message(message.chat.id, "تم إنشاء التطبيق بنجاح.", reply_markup=create_back_button())
    else:
        bot.send_message(message.chat.id, "فشل في إنشاء التطبيق. تحقق من صحة مفتاح API أو اسم التطبيق.", reply_markup=create_back_button())

# Function to toggle safe mode
def toggle_safe_mode(call):
    user_id = call.from_user.id
    safe_mode[user_id] = not safe_mode.get(user_id, False)
    status = "مفعل ✅" if safe_mode[user_id] else "معطل ❌"
    bot.edit_message_text(f"الوضع الآمن: {status}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_main_buttons())

# Function to handle callback queries
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "add_api":
        add_api(call)
    elif call.data == "list_accounts":
        list_accounts(call)
    elif call.data.startswith("select_account_"):
        account_index = int(call.data.split("_")[-1])
        bot.edit_message_text("خيارات التحكم في الحساب:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_account_control_buttons(account_index))
    elif call.data.startswith("delete_app_"):
        account_index = int(call.data.split("_")[2])
        delete_app(call, account_index)
    elif call.data.startswith("create_app_"):
        account_index = int(call.data.split("_")[2])
        create_app(call, account_index)
    elif call.data == "toggle_safe_mode":
        toggle_safe_mode(call)
    elif call.data == "go_back":
        bot.edit_message_text("اهلا وسهلا نورتنا اختار من بين الازرار ماذا تريد", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_main_buttons())

# Start the bot
bot.polling()
