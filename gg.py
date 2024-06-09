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
                        api_keys TEXT[]
                      );''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS self_deleting_apps (
                        app_name TEXT PRIMARY KEY,
                        minutes INTEGER,
                        start_time TIMESTAMPTZ
                      );''')
    connection.commit()

create_tables()

# دالة لحفظ البيانات إلى قاعدة البيانات
def save_account(user_id, api_key):
    cursor.execute('''INSERT INTO accounts (user_id, api_keys)
                      VALUES (%s, ARRAY[%s])
                      ON CONFLICT (user_id) DO UPDATE
                      SET api_keys = array_append(accounts.api_keys, %s);''', (user_id, api_key, api_key))
    connection.commit()

# دالة لتحميل المفاتيح للمستخدم
def load_accounts(user_id):
    cursor.execute('SELECT api_keys FROM accounts WHERE user_id = %s;', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else []

# دالة لحفظ تطبيقات المستخدم
def save_self_deleting_app(app_name, minutes):
    cursor.execute('''INSERT INTO self_deleting_apps (app_name, minutes, start_time)
                      VALUES (%s, %s, %s);''', (app_name, minutes, datetime.now(pytz.timezone('Asia/Baghdad'))))
    connection.commit()

# دالة لتحميل تطبيقات المستخدم
def load_self_deleting_apps(user_id):
    cursor.execute('SELECT app_name, minutes, start_time FROM self_deleting_apps WHERE user_id = %s;', (user_id,))
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
    keys = load_accounts(user_id)
    count = len(keys)
    bot.reply_to(message, f"لديك {count} مفتاح API مخزن.")

# عرض المفاتيح المخزنة
@bot.message_handler(func=lambda message: message.text == 'عرض المفاتيح')
def show_keys(message):
    user_id = message.from_user.id
    keys = load_accounts(user_id)
    if keys:
        key_list = '\n'.join(keys)
        bot.reply_to(message, f"مفاتيح API المخزنة الخاصة بك:\n{key_list}")
    else:
        bot.reply_to(message, "لم تقم بتخزين أي مفاتيح API حتى الآن.")

# عرض حساب المستخدم وتطبيقاته
@bot.message_handler(func=lambda message: message.text == 'عرض حسابي')
def show_account(message):
    user_id = message.from_user.id
    apps = load_self_deleting_apps(user_id)
    if apps:
        app_list = '\n'.join([f"{app[0]} - {app[1]} دقائق" for app in apps])
        bot.reply_to(message, f"تطبيقاتك المخزنة:\n{app_list}")
    else:
        bot.reply_to(message, "لم تقم بتخزين أي تطبيقات حتى الآن.")

# التعامل مع الرسائل غير المعروفة
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "لا أفهم رسالتك. يرجى استخدام الأزرار.")

# تشغيل البوت
bot.polling()
