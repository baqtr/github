import os
import telebot
import psycopg2
from telebot import types

# استيراد توكن البوت من المتغيرات البيئية
bot_token = "7031770762:AAF-BrYHNEcX8VyGBzY1mastEG3SWod4_uI"
database_url = os.getenv("DATABASE_URL", "postgres://u7sp4pi4bkcli5:p8084ef55d7306694913f43fe18ae8f1e24bf9d4c33b1bdae2e9d49737ea39976@ec2-18-210-84-56.compute-1.amazonaws.com:5432/dbdstma1phbk1e")

# إنشاء كائن البوت
bot = telebot.TeleBot(bot_token)

# إعداد قاعدة البيانات
connection = psycopg2.connect(database_url)
cursor = connection.cursor()

# دالة لإنشاء الجداول إذا لم تكن موجودة
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                        user_id BIGINT PRIMARY KEY,
                        api_key TEXT
                      );''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS self_deleting_apps (
                        app_name TEXT,
                        api_key TEXT,
                        minutes INTEGER,
                        start_time TIMESTAMPTZ,
                        PRIMARY KEY (app_name, api_key)
                      );''')
    connection.commit()

create_tables()

# دالة لحفظ البيانات إلى قاعدة البيانات
def save_account(user_id, api_key):
    cursor.execute('''INSERT INTO accounts (user_id, api_key)
                      VALUES (%s, %s)
                      ON CONFLICT (user_id) DO UPDATE
                      SET api_key = excluded.api_key;''', (user_id, api_key))
    connection.commit()

# دالة لتحميل المفتاح للمستخدم
def load_account(user_id):
    cursor.execute('SELECT api_key FROM accounts WHERE user_id = %s;', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None

# دالة لحفظ تطبيق المستخدم
def save_self_deleting_app(app_name, api_key, minutes):
    cursor.execute('''INSERT INTO self_deleting_apps (app_name, api_key, minutes, start_time)
                      VALUES (%s, %s, %s, now());''', (app_name, api_key, minutes))
    connection.commit()

# دالة لتحميل تطبيقات المستخدم
def load_self_deleting_apps(api_key):
    cursor.execute('SELECT app_name, minutes, start_time FROM self_deleting_apps WHERE api_key = %s;', (api_key,))
    return cursor.fetchall()

# إنشاء قائمة الأزرار
def create_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    count_button = types.KeyboardButton('عدد المفاتيح')
    show_button = types.KeyboardButton('عرض المفاتيح')
    account_button = types.KeyboardButton('عرض حسابي')
    keyboard.add(count_button, show_button, account_button)
    return keyboard

# عرض عدد المفاتيح المخزنة
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "مرحبًا بك! اختر ما ترغب في القيام به:", reply_markup=create_keyboard())

# عرض عدد المفاتيح المخزنة
@bot.message_handler(func=lambda message: message.text == 'عدد المفاتيح')
def count_keys(message):
    user_id = message.from_user.id
    api_key = load_account(user_id)
    if api_key:
        bot.reply_to(message, "لديك مفتاح API مخزن.")
    else:
        bot.reply_to(message, "لم تقم بتخزين أي مفتاح API حتى الآن.")

# عرض المفاتيح المخزنة
@bot.message_handler(func=lambda message: message.text == 'عرض المفاتيح')
def show_keys(message):
    user_id = message.from_user.id
    api_key = load_account(user_id)
    if api_key:
        apps = load_self_deleting_apps(api_key)
        if apps:
            app_list = '\n'.join([f"{app[0]} - {app[1]} دقائق" for app in apps])
            bot.reply_to(message, f"تطبيقاتك المخزنة:\n{app_list}")
        else:
            bot.reply_to(message, "لم تقم بتخزين أي تطبيقات حتى الآن.")
    else:
        bot.reply_to(message, "لم تقم بتخزين أي مفتاح API حتى الآن.")

# عرض حساب المستخدم وتطبيقاته
@bot.message_handler(func=lambda message: message.text == 'عرض حسابي')
def show_account(message):
    user_id = message.from_user.id
    api_key = load_account(user_id)
    if api_key:
        bot.reply_to(message, f"مفتاح API المخزن: {api_key}")
    else:
        bot.reply_to(message, "لم تقم بتخزين أي مفتاح API حتى الآن.")

# التعامل مع الرسائل غير المعروفة
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "لا أفهم رسالتك. يرجى استخدام الأزرار.")

# تشغيل البوت
bot.polling()
