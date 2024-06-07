import os
import telebot
import requests
import threading
import time
import zipfile
import tempfile
import random
import string
import shutil
from datetime import datetime, timedelta
import pytz
from github import Github

# استيراد توكن البوت من المتغيرات البيئية
bot_token = "7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20"
github_token = "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"
# إنشاء كائن البوت
bot = telebot.TeleBot(bot_token)

# الهيروكو API
HEROKU_BASE_URL = 'https://api.heroku.com'

# قائمة التطبيقات المجدولة للحذف الذاتي
self_deleting_apps = {}
g = Github(github_token)
# قائمة التطبيقات المجدولة للحذف الذاتي
self_deleting_apps = {}

# تخزين حسابات المستخدم
user_accounts = {}

# دالة لإنشاء الأزرار وتخصيصها
def create_main_buttons():
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton("إضافة حساب ➕", callback_data="add_account")
    button2 = telebot.types.InlineKeyboardButton("حساباتك 🗂️", callback_data="list_accounts")
    button3 = telebot.types.InlineKeyboardButton("قسم جيتهاب 🛠️", callback_data="github_section")
    markup.add(button1, button2)
    markup.add(button3)
    return markup

def create_github_control_buttons():
    markup = telebot.types.InlineKeyboardMarkup()
    publish_repo_button = telebot.types.InlineKeyboardButton("نشر مستودع 📤", callback_data="publish_repo")
    list_repos_button = telebot.types.InlineKeyboardButton(" عرض المستودعات 📂", callback_data="list_github_repos")
    markup.row(publish_repo_button)
    markup.add(list_repos_button)
    markup.add(telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="go_back"))
    return markup

# دالة لإنشاء زر العودة
def create_back_button():
    markup = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="go_back")
    markup.add(back_button)
    return markup

# دالة لإنشاء أزرار التحكم بالحسابات
def create_account_control_buttons(account_index):
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton("جلب تطبيقات هيروكو 📦", callback_data=f"list_heroku_apps_{account_index}")
    button2 = telebot.types.InlineKeyboardButton("الحذف الذاتي ⏲️", callback_data=f"self_delete_app_{account_index}")
    button3 = telebot.types.InlineKeyboardButton("الوقت المتبقي ⏳", callback_data="remaining_time")
    markup.add(button1) 
    markup.add(button2)
    markup.add(button3)
    markup.add(telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="list_accounts"))
    return markup

# دالة لمعالجة الطلبات الواردة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in user_accounts:
        user_accounts[user_id] = []
    bot.send_message(message.chat.id, "اهلا وسهلا نورتنا اختار من بين الازرار ماذا تريد", reply_markup=create_main_buttons())

# دالة لإضافة حساب جديد
def add_account(call):
    msg = bot.edit_message_text("يرجى إرسال مفتاح API الخاص بحساب Heroku:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
    bot.register_next_step_handler(msg, handle_new_account)

def handle_new_account(message):
    api_key = message.text.strip()
    user_id = message.from_user.id
    if api_key in [account['api_key'] for account in user_accounts[user_id]]:
        bot.send_message(message.chat.id, "هذا الحساب مضاف مسبقًا.", reply_markup=create_main_buttons())
    elif validate_heroku_api_key(api_key):
        user_accounts[user_id].append({'api_key': api_key})
        bot.send_message(message.chat.id, "تمت إضافة حساب Heroku بنجاح!", reply_markup=create_main_buttons())
    else:
        bot.send_message(message.chat.id, "مفتاح API غير صحيح. يرجى المحاولة مرة أخرى.", reply_markup=create_main_buttons())
# التحقق من صحة مفتاح API
def validate_heroku_api_key(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    response = requests.get(f'{HEROKU_BASE_URL}/apps', headers=headers)
    return response.status_code == 200

# عرض حسابات المستخدم
def list_accounts(call):
    user_id = call.from_user.id
    if user_id in user_accounts and user_accounts[user_id]:
        accounts_list = "\n".join([f"حساب {index + 1}: `{get_heroku_account_name(account['api_key'])}`" for index, account in enumerate(user_accounts[user_id])])
        markup = telebot.types.InlineKeyboardMarkup()
        for index in range(len(user_accounts[user_id])):
            account_name = get_heroku_account_name(user_accounts[user_id][index]['api_key'])
            markup.add(telebot.types.InlineKeyboardButton(f"{account_name}", callback_data=f"select_account_{index}"))
        markup.add(telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="go_back"))
        bot.edit_message_text(f"حساباتك:\n{accounts_list}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.edit_message_text("لا توجد حسابات مضافة.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

# جلب اسم حساب هيروكو
def get_heroku_account_name(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    response = requests.get(f'{HEROKU_BASE_URL}/account', headers=headers)
    if response.status_code == 200:
        return response.json().get('email', 'Unknown')
    return 'Unknown'

# دالة لجلب تطبيقات هيروكو
def list_heroku_apps(call):
    account_index = int(call.data.split("_")[-1])
    user_id = call.from_user.id
    if not user_accounts[user_id]:
        bot.edit_message_text("لا توجد حسابات مضافة. يرجى إضافة حساب أولاً.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
        return

    headers = {
        'Authorization': f'Bearer {user_accounts[user_id][account_index]["api_key"]}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    bot.edit_message_text("جلب التطبيقات... ⬛⬜ 0%", chat_id=call.message.chat.id, message_id=call.message.message_id)
    time.sleep(2)
    response = requests.get(f'{HEROKU_BASE_URL}/apps', headers=headers)
    if response.status_code == 200:
        apps = response.json()
        apps_list = "\n".join([f"`{app['name']}`" for app in apps])
        bot.edit_message_text("جلب التطبيقات... ⬛⬛ 50%", chat_id=call.message.chat.id, message_id=call.message.message_id)
        time.sleep(2)
        bot.edit_message_text(f"التطبيقات المتاحة في هيروكو:\n{apps_list}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button(), parse_mode='Markdown')
    else:
        bot.edit_message_text("حدث خطأ في جلب التطبيقات من هيروكو.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

# دالة لمعالجة النقرات على الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "add_account":
        add_account(call)
    elif call.data == "list_accounts":
        list_accounts(call)
    elif call.data.startswith("select_account_"):
        account_index = int(call.data.split("_")[-1])
        bot.edit_message_text(f"إدارة حساب {account_index + 1}:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_account_control_buttons(account_index))
    elif call.data.startswith("list_heroku_apps_"):
        list_heroku_apps(call)
    elif call.data.startswith("self_delete_app_"):
        account_index = int(call.data.split("_")[-1])
        msg = bot.edit_message_text("يرجى إرسال اسم التطبيق للحذف الذاتي:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
        bot.register_next_step_handler(msg, lambda m: handle_app_name_for_self_deletion(m, account_index))
    elif call.data == "remaining_time":
        show_remaining_time(call)
    elif call.data == "go_back":
        bot.edit_message_text("اهلا وسهلا نورتنا اختار من بين الازرار ماذا تريد", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_main_buttons())
    elif call.data == "github_section":
        bot.edit_message_text("قسم جيتهاب 🛠️", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_github_control_buttons())
    elif call.data == "publish_repo":
        msg = bot.edit_message_text("يرجى إرسال اسم المستودع (repository) للرفع:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
        bot.register_next_step_handler(msg, handle_publish_repo)
    elif call.data == "list_github_repos":
        list_github_repos(call)

# دالة لمعالجة اسم التطبيق للحذف الذاتي
def handle_app_name_for_self_deletion(message, account_index):
    app_name = message.text.strip()
    user_id = message.from_user.id
    if user_id not in self_deleting_apps:
        self_deleting_apps[user_id] = {}

    if app_name in self_deleting_apps[user_id]:
        bot.send_message(message.chat.id, "تم جدولة هذا التطبيق مسبقًا للحذف الذاتي.", reply_markup=create_main_buttons())
        return

    self_deleting_apps[user_id][app_name] = {
        "account_index": account_index,
        "delete_time": datetime.now(pytz.utc) + timedelta(hours=1)  # اضبط الوقت هنا كما تريد
    }
    bot.send_message(message.chat.id, f"تم جدولة تطبيق `{app_name}` للحذف الذاتي بعد ساعة.", reply_markup=create_main_buttons(), parse_mode='Markdown')

    # بدء مؤقت الحذف الذاتي
    threading.Thread(target=self_delete_app_timer, args=(user_id, app_name)).start()

# دالة مؤقت الحذف الذاتي
def self_delete_app_timer(user_id, app_name):
    while True:
        time.sleep(10)
        if app_name not in self_deleting_apps[user_id]:
            break

        delete_time = self_deleting_apps[user_id][app_name]["delete_time"]
        if datetime.now(pytz.utc) >= delete_time:
            account_index = self_deleting_apps[user_id][app_name]["account_index"]
            api_key = user_accounts[user_id][account_index]["api_key"]
            delete_heroku_app(api_key, app_name)
            del self_deleting_apps[user_id][app_name]
            break

# دالة لحذف تطبيق هيروكو
def delete_heroku_app(api_key, app_name):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    response = requests.delete(f'{HEROKU_BASE_URL}/apps/{app_name}', headers=headers)
    if response.status_code == 202:
        print(f"تم حذف تطبيق {app_name} بنجاح.")
    else:
        print(f"فشل حذف تطبيق {app_name}. رمز الاستجابة: {response.status_code}")

# دالة لعرض الوقت المتبقي للحذف الذاتي
def show_remaining_time(call):
    user_id = call.from_user.id
    if user_id not in self_deleting_apps or not self_deleting_apps[user_id]:
        bot.edit_message_text("لا توجد تطبيقات مجدولة للحذف الذاتي.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
        return

    remaining_times = []
    for app_name, data in self_deleting_apps[user_id].items():
        remaining_time = data["delete_time"] - datetime.now(pytz.utc)
        remaining_times.append(f"`{app_name}`: {remaining_time}")

    remaining_times_text = "\n".join(remaining_times)
    bot.edit_message_text(f"الأوقات المتبقية للتطبيقات المجدولة للحذف الذاتي:\n{remaining_times_text}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button(), parse_mode='Markdown')

# دالة لمعالجة نشر المستودع
def handle_publish_repo(message):
    repo_name = message.text.strip()
    user_id = message.from_user.id

    if not user_accounts[user_id]:
        bot.send_message(message.chat.id, "لا توجد حسابات مضافة. يرجى إضافة حساب أولاً.", reply_markup=create_main_buttons())
        return

    # مؤقت لنشر المستودع
    msg = bot.send_message(message.chat.id, "جاري رفع المستودع... ⬛⬜ 0%", reply_markup=create_back_button())
    time.sleep(2)

    # افتراضيا يقوم بنشر مستودع فارغ كمثال
    user = g.get_user()
    repo = user.create_repo(repo_name)

    bot.edit_message_text("جاري رفع المستودع... ⬛⬛ 50%", chat_id=message.chat.id, message_id=msg.message_id)
    time.sleep(2)
    
    bot.edit_message_text(f"تم نشر المستودع `{repo_name}` بنجاح على GitHub!", chat_id=message.chat.id, message_id=msg.message_id, reply_markup=create_main_buttons(), parse_mode='Markdown')

# دالة لعرض المستودعات في GitHub
def list_github_repos(call):
    user = g.get_user()
    repos = user.get_repos()
    repos_list = "\n".join([f"{repo.name}" for repo in repos])

    bot.edit_message_text(f"المستودعات المتاحة في GitHub:\n{repos_list}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

# بدء تشغيل البوت
bot.polling()
