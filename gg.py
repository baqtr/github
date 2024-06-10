import os
import telebot
import psycopg2
import requests
from telebot import types

# استيراد توكن البوت من المتغيرات البيئية
bot_token = "7031770762:AAF-BrYHNEcX8VyGBzY1mastEG3SWod4_uI"
database_url = os.getenv("DATABASE_URL", "postgres://u7sp4pi4bkcli5:p8084ef55d7306694913f43fe18ae8f1e24bf9d4c33b1bdae2e9d49737ea39976@ec2-18-210-84-56.compute-1.amazonaws.com:5432/dbdstma1phbk1e")

# إنشاء كائن البوت
bot = telebot.TeleBot(bot_token)

# إعداد قاعدة البيانات
connection = psycopg2.connect(database_url)
cursor = connection.cursor()

# دالة لإنشاء جدول الحسابات والتطبيقات إذا لم تكن موجودة
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        account_name TEXT,
                        api_key TEXT UNIQUE
                      );''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS applications (
                        id SERIAL PRIMARY KEY,
                        account_id INTEGER REFERENCES accounts(id),
                        app_name TEXT
                      );''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT
                      );''')
    connection.commit()

create_tables()

# دالة لحفظ المستخدم في قاعدة البيانات
def save_user(user_id, username):
    cursor.execute('''INSERT INTO users (user_id, username)
                      VALUES (%s, %s)
                      ON CONFLICT (user_id) DO NOTHING;''', (user_id, username))
    connection.commit()

# دالة لحفظ الحساب في قاعدة البيانات
def save_account(user_id, account_name, api_key):
    cursor.execute('''INSERT INTO accounts (user_id, account_name, api_key)
                      VALUES (%s, %s, %s);''', (user_id, account_name, api_key))
    connection.commit()

# دالة لجلب الحسابات من قاعدة البيانات
def load_accounts(user_id):
    cursor.execute('SELECT id, account_name, api_key FROM accounts WHERE user_id = %s;', (user_id,))
    return cursor.fetchall()

# دالة لحفظ التطبيقات في قاعدة البيانات
def save_application(account_id, app_name):
    cursor.execute('''INSERT INTO applications (account_id, app_name)
                      VALUES (%s, %s);''', (account_id, app_name))
    connection.commit()

# دالة لجلب التطبيقات من قاعدة البيانات
def load_applications(account_id):
    cursor.execute('SELECT app_name FROM applications WHERE account_id = %s;', (account_id,))
    return cursor.fetchall()

# دالة لحذف التطبيق من قاعدة البيانات
def delete_application(account_id, app_name):
    cursor.execute('DELETE FROM applications WHERE account_id = %s AND app_name = %s;', (account_id, app_name))
    connection.commit()

# دالة للتحقق من صحة API Key
def verify_api_key(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/vnd.heroku+json; version=3"
    }
    response = requests.get("https://api.heroku.com/account", headers=headers)
    return response.status_code == 200

# دالة لجلب قائمة التطبيقات من هيروكو
def get_heroku_apps(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/vnd.heroku+json; version=3"
    }
    response = requests.get("https://api.heroku.com/apps", headers=headers)
    if response.status_code == 200:
        return [app["name"] for app in response.json()]
    else:
        return []

# دالة لإنشاء قائمة الأزرار
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_account_button = types.KeyboardButton('إضافة حساب')
    view_accounts_button = types.KeyboardButton('حساباتك')
    storage_status_button = types.KeyboardButton('حالة التخزين')
    markup.add(add_account_button, view_accounts_button, storage_status_button)
    return markup

# عرض القائمة الرئيسية في بداية الدردشة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.from_user.id, message.from_user.username)
    bot.send_message(message.chat.id, "مرحبًا بك! اختر ما ترغب في القيام به:", reply_markup=main_menu())

# إضافة حساب جديد
@bot.message_handler(func=lambda message: message.text == 'إضافة حساب')
def add_account(message):
    msg = bot.reply_to(message, "قم بإرسال اسم الحساب.")
    bot.register_next_step_handler(msg, process_account_name)

def process_account_name(message):
    account_name = message.text
    msg = bot.reply_to(message, "الآن قم بإرسال API Key.")
    bot.register_next_step_handler(msg, process_api_key, account_name)

def process_api_key(message, account_name):
    api_key = message.text
    if verify_api_key(api_key):
        save_account(message.from_user.id, account_name, api_key)
        bot.reply_to(message, "تمت إضافة الحساب بنجاح.")
        # جلب التطبيقات وحفظها في قاعدة البيانات
        account_id = load_accounts(message.from_user.id)[-1][0]
        apps = get_heroku_apps(api_key)
        for app in apps:
            save_application(account_id, app)
    else:
        bot.reply_to(message, "API Key غير صالح. يرجى المحاولة مرة أخرى.")

# عرض الحسابات المضافة
@bot.message_handler(func=lambda message: message.text == 'حساباتك')
def view_accounts(message):
    try:
        accounts = load_accounts(message.from_user.id)
        if accounts:
            for account in accounts:
                markup = types.InlineKeyboardMarkup()
                view_apps_button = types.InlineKeyboardButton('عرض التطبيقات', callback_data=f"view_apps:{account[0]}")
                delete_app_button = types.InlineKeyboardButton('حذف تطبيق', callback_data=f"delete_app:{account[0]}")
                markup.add(view_apps_button, delete_app_button)
                bot.send_message(message.chat.id, f"الحساب: {account[1]}", reply_markup=markup)
        else:
            bot.reply_to(message, "لم تقم بإضافة أي حسابات بعد.")
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ أثناء جلب الحسابات: {e}")

# عرض التطبيقات المضافة لحساب معين
@bot.callback_query_handler(func=lambda call: call.data.startswith('view_apps'))
def view_apps(call):
    account_id = call.data.split(':')[1]
    applications = load_applications(account_id)
    if applications:
        app_list = '\n'.join([app[0] for app in applications])
        bot.send_message(call.message.chat.id, f"التطبيقات:\n{app_list}")
    else:
        bot.send_message(call.message.chat.id, "لا توجد تطبيقات.")

# حذف تطبيق لحساب معين
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_app'))
def delete_app(call):
    account_id = call.data.split(':')[1]
    msg = bot.send_message(call.message.chat.id, "قم بإرسال اسم التطبيق الذي تريد حذفه.")
    bot.register_next_step_handler(msg, process_delete_app, account_id)

def process_delete_app(message, account_id):
    app_name = message.text
    applications = load_applications(account_id)
    if (app_name,) in applications:
        delete_application(account_id, app_name)
        bot.reply_to(message, f"تم حذف التطبيق: {app_name}")
    else:
        bot.reply_to(message, "اسم التطبيق غير موجود. يرجى المحاولة مرة أخرى.")

# عرض حالة التخزين
@bot.message_handler(func=lambda message: message.text == 'حالة التخزين')
def storage_status(message):
    try:
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM accounts;")
        account_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM applications;")
        app_count = cursor.fetchone()[0]
        status = f"عدد المستخدمين: {user_count}\nعدد الحسابات: {account_count}\nعدد التطبيقات: {app_count}"
        bot.send_message(message.chat.id, status)
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ أثناء جلب حالة التخزين: {e}")

# التعامل مع الرسائل غير المعروفة
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "يرجى استخدام الأزرار.")

# تشغيل البوت
bot.polling()
