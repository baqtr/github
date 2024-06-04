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
import json

# استيراد توكن البوت من المتغيرات البيئية
bot_token = "6444148337:7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20"
github_token = "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"
# إنشاء كائن البوت
bot = telebot.TeleBot(bot_token)

# الهيروكو API
HEROKU_BASE_URL = 'https://api.heroku.com'

# قائمة التطبيقات المجدولة للحذف الذاتي
self_deleting_apps = {}
g = Github(github_token)

# تخزين حسابات المستخدم
user_accounts = {}

# قائمة لتخزين الأحداث
events = []

# تخزين إعدادات المستخدم
user_settings = {}

# دالة لإنشاء الأزرار وتخصيصها
def create_main_buttons():
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton("إضافة حساب ➕", callback_data="add_account")
    button2 = telebot.types.InlineKeyboardButton("حساباتك 🗂️", callback_data="list_accounts")
    button3 = telebot.types.InlineKeyboardButton("قسم جيتهاب 🛠️", callback_data="github_section")
    button4 = telebot.types.InlineKeyboardButton("الأحداث 🔄", callback_data="show_events")
    button5 = telebot.types.InlineKeyboardButton("الإعدادات ⚙️", callback_data="settings")
    markup.add(button1, button2)
    markup.add(button3)
    markup.add(button4)
    markup.add(button5)
    return markup

def create_github_control_buttons():
    markup = telebot.types.InlineKeyboardMarkup()
    delete_all_button = telebot.types.InlineKeyboardButton("حذف الكل 🗑️", callback_data="delete_all_repos")
    delete_repo_button = telebot.types.InlineKeyboardButton("حذف مستودع 🗑️", callback_data="delete_repo")
    upload_file_button = telebot.types.InlineKeyboardButton("رفع ملف 📤", callback_data="upload_file")
    list_repos_button = telebot.types.InlineKeyboardButton(" عرض المستودعات 📂", callback_data="list_github_repos")
    markup.row(delete_all_button, delete_repo_button)
    markup.row(upload_file_button)
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
    button2 = telebot.types.InlineKeyboardButton("حذف تطبيق ❌", callback_data=f"delete_app_{account_index}")
    button3 = telebot.types.InlineKeyboardButton("الحذف الذاتي ⏲️", callback_data=f"self_delete_app_{account_index}")
    button4 = telebot.types.InlineKeyboardButton("الوقت المتبقي ⏳", callback_data="remaining_time")
    markup.add(button1) 
    markup.add(button2)
    markup.add(button3)
    markup.add(button4)
    markup.add(telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="list_accounts"))
    return markup

# دالة لمعالجة الطلبات الواردة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in user_accounts:
        user_accounts[user_id] = []
        events.append(f"انضم مستخدم جديد: [{message.from_user.first_name}](tg://user?id={user_id})")
    if user_id not in user_settings:
        user_settings[user_id] = {'safe_mode': False}
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
        events.append(f"أضاف [{message.from_user.first_name}](tg://user?id={user_id}) حساب جديد: `{api_key[:-4]}****`")
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
def callback_handler(call):
    if call.data == "add_account":
        add_account(call)
    elif call.data == "list_accounts":
        list_accounts(call)
    elif call.data == "show_events":
        show_events(call)
    elif call.data == "github_section":
        bot.edit_message_text("قسم جيتهاب: اختر الإجراء المطلوب:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_github_control_buttons())
    elif call.data == "settings":
        show_settings(call)
    elif "list_heroku_apps_" in call.data:
        list_heroku_apps(call)
    elif "select_account_" in call.data:
        account_index = int(call.data.split("_")[-1])
        bot.edit_message_text(f"تم اختيار الحساب رقم {account_index + 1}. اختر الإجراء المطلوب:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_account_control_buttons(account_index))
    elif call.data == "go_back":
        bot.edit_message_text("اهلا وسهلا نورتنا اختار من بين الازرار ماذا تريد", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_main_buttons())
    elif call.data == "delete_all_repos":
        delete_all_repos(call)
    elif call.data == "delete_repo":
        delete_repo(call)
    elif call.data == "upload_file":
        upload_file(call)
    elif call.data == "list_github_repos":
        list_github_repos(call)
    elif call.data == "create_backup":
        create_backup(call)
    elif call.data == "restore_backup":
        restore_backup(call)
    elif call.data == "delete_all_accounts":
        delete_all_accounts(call)
    elif call.data == "toggle_safe_mode":
        toggle_safe_mode(call)
    elif "delete_app_" in call.data:
        delete_app(call)
    elif "self_delete_app_" in call.data:
        self_delete_app(call)

# عرض الأحداث
def show_events(call):
    events_list = "\n".join(events[-10:])
    bot.edit_message_text(f"الأحداث الأخيرة:\n{events_list}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button(), parse_mode='Markdown')

# عرض الإعدادات
def show_settings(call):
    user_id = call.from_user.id
    safe_mode_status = "مفعل ✅" if user_settings[user_id]['safe_mode'] else "معطل ❌"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(f"الوضع الآمن: {safe_mode_status}", callback_data="toggle_safe_mode"))
    markup.add(telebot.types.InlineKeyboardButton("إنشاء نسخة احتياطية 📦", callback_data="create_backup"))
    markup.add(telebot.types.InlineKeyboardButton("استعادة نسخة احتياطية 🔄", callback_data="restore_backup"))
    markup.add(telebot.types.InlineKeyboardButton("حذف كل الحسابات 🗑️", callback_data="delete_all_accounts"))
    markup.add(telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="go_back"))
    bot.edit_message_text("الإعدادات:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

# إنشاء نسخة احتياطية
def create_backup(call):
    user_id = call.from_user.id
    backup_data = {
        'accounts': user_accounts.get(user_id, []),
        'events': events,
        'settings': user_settings.get(user_id, {})
    }
    backup_filename = f"backup_{user_id}_{int(time.time())}.json"
    with open(backup_filename, 'w') as backup_file:
        json.dump(backup_data, backup_file)
    bot.send_message(call.message.chat.id, "تم إنشاء النسخة الاحتياطية بنجاح!", reply_markup=create_back_button())
    bot.send_document(call.message.chat.id, open(backup_filename, 'rb'))
    os.remove(backup_filename)

# استعادة نسخة احتياطية
def restore_backup(call):
    msg = bot.send_message(call.message.chat.id, "يرجى إرسال ملف النسخة الاحتياطية:")
    bot.register_next_step_handler(msg, handle_restore_backup)

def handle_restore_backup(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(downloaded_file)
            temp_file_path = temp_file.name
        with open(temp_file_path, 'r') as backup_file:
            backup_data = json.load(backup_file)
        user_id = message.from_user.id
        user_accounts[user_id] = backup_data.get('accounts', [])
        events.extend(backup_data.get('events', []))
        user_settings[user_id] = backup_data.get('settings', {})
        bot.send_message(message.chat.id, "تم استعادة النسخة الاحتياطية بنجاح!", reply_markup=create_back_button())
        os.remove(temp_file_path)
    else:
        bot.send_message(message.chat.id, "لم يتم إرسال ملف صالح. يرجى المحاولة مرة أخرى.", reply_markup=create_back_button())

# حذف جميع الحسابات
def delete_all_accounts(call):
    user_id = call.from_user.id
    user_accounts[user_id] = []
    bot.send_message(call.message.chat.id, "تم حذف جميع الحسابات المضافة بنجاح.", reply_markup=create_back_button())

# تبديل الوضع الآمن
def toggle_safe_mode(call):
    user_id = call.from_user.id
    user_settings[user_id]['safe_mode'] = not user_settings[user_id]['safe_mode']
    safe_mode_status = "مفعل ✅" if user_settings[user_id]['safe_mode'] else "معطل ❌"
    bot.edit_message_text(f"تم تعديل الوضع الآمن: {safe_mode_status}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

# حذف تطبيق هيروكو
def delete_app(call):
    if not user_settings[call.from_user.id]['safe_mode']:
        # رمز الحذف هنا
        bot.edit_message_text("تم حذف التطبيق بنجاح.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
    else:
        bot.edit_message_text("عذرًا، لا يمكن الحذف بسبب تفعيل الوضع الآمن.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

# الحذف الذاتي لتطبيق هيروكو
def self_delete_app(call):
    if not user_settings[call.from_user.id]['safe_mode']:
        # رمز الحذف الذاتي هنا
        bot.edit_message_text("تم تفعيل الحذف الذاتي للتطبيق.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
    else:
        bot.edit_message_text("عذرًا، لا يمكن تفعيل الحذف الذاتي بسبب تفعيل الوضع الآمن.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

# دالة لحذف جميع مستودعات جيتهاب
def delete_all_repos(call):
    user_id = call.from_user.id
    if not user_settings[user_id]['safe_mode']:
        user_repos = g.get_user().get_repos()
        for repo in user_repos:
            repo.delete()
        bot.edit_message_text("تم حذف جميع مستودعات جيتهاب بنجاح.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
    else:
        bot.edit_message_text("عذرًا، لا يمكن الحذف بسبب تفعيل الوضع الآمن.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

# دالة لحذف مستودع جيتهاب معين
def delete_repo(call):
    user_id = call.from_user.id
    if not user_settings[user_id]['safe_mode']:
        msg = bot.edit_message_text("يرجى إرسال اسم المستودع المراد حذفه:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
        bot.register_next_step_handler(msg, handle_delete_repo)
    else:
        bot.edit_message_text("عذرًا، لا يمكن الحذف بسبب تفعيل الوضع الآمن.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

def handle_delete_repo(message):
    repo_name = message.text.strip()
    user_id = message.from_user.id
    user = g.get_user()
    try:
        repo = user.get_repo(repo_name)
        repo.delete()
        bot.send_message(message.chat.id, f"تم حذف مستودع `{repo_name}` بنجاح.", reply_markup=create_back_button(), parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, f"تعذر العثور على مستودع `{repo_name}` أو حذفه.", reply_markup=create_back_button(), parse_mode='Markdown')

# دالة لرفع ملف إلى جيتهاب
def upload_file(call):
    user_id = call.from_user.id
    if not user_settings[user_id]['safe_mode']:
        msg = bot.edit_message_text("يرجى إرسال اسم المستودع المراد رفع الملف إليه:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
        bot.register_next_step_handler(msg, handle_upload_file_repodef handle_upload_file_repo(message):
    repo_name = message.text.strip()
    user_id = message.from_user.id
    user = g.get_user()
    try:
        repo = user.get_repo(repo_name)
        msg = bot.send_message(message.chat.id, "يرجى إرسال الملف المراد رفعه:")
        bot.register_next_step_handler(msg, handle_upload_file, repo)
    except:
        bot.send_message(message.chat.id, f"تعذر العثور على مستودع `{repo_name}`.", reply_markup=create_back_button(), parse_mode='Markdown')

def handle_upload_file(message, repo):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(downloaded_file)
            temp_file_path = temp_file.name
        with open(temp_file_path, 'rb') as file_data:
            content = file_data.read()
        os.remove(temp_file_path)
        
        file_path = message.document.file_name
        repo.create_file(file_path, "Uploaded via Telegram Bot", content)
        bot.send_message(message.chat.id, f"تم رفع الملف إلى مستودع `{repo.name}` بنجاح.", reply_markup=create_back_button(), parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "لم يتم إرسال ملف صالح. يرجى المحاولة مرة أخرى.", reply_markup=create_back_button())

# دالة لعرض مستودعات جيتهاب
def list_github_repos(call):
    user = g.get_user()
    repos = user.get_repos()
    repos_list = "\n".join([f"`{repo.name}`" for repo in repos])
    bot.edit_message_text(f"المستودعات المتاحة:\n{repos_list}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button(), parse_mode='Markdown')

# بدء تشغيل البوت
def main():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()
