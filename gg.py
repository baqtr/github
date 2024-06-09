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
                        username TEXT
                      );''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS apps (
                        app_name TEXT PRIMARY KEY,
                        user_id BIGINT,
                        FOREIGN KEY (user_id) REFERENCES accounts(user_id)
                      );''')
    connection.commit()

create_tables()

# دالة لحفظ الحساب في قاعدة البيانات
def save_account(user_id, username):
    cursor.execute('''INSERT INTO accounts (user_id, username)
                      VALUES (%s, %s)
                      ON CONFLICT (user_id) DO NOTHING;''', (user_id, username))
    connection.commit()

# دالة لحفظ التطبيق في قاعدة البيانات
def save_app(app_name, user_id):
    cursor.execute('''INSERT INTO apps (app_name, user_id)
                      VALUES (%s, %s)
                      ON CONFLICT (app_name) DO NOTHING;''', (app_name, user_id))
    connection.commit()

# دالة لحذف التطبيق من قاعدة البيانات
def delete_app(app_name):
    cursor.execute('''DELETE FROM apps WHERE app_name = %s;''', (app_name,))
    connection.commit()

# دالة لتحميل التطبيقات للمستخدم
def load_apps(user_id):
    cursor.execute('SELECT app_name FROM apps WHERE user_id = %s;', (user_id,))
    return cursor.fetchall()

# عرض التطبيقات المخزنة للمستخدم
@bot.message_handler(func=lambda message: message.text == 'عرض التطبيقات')
def show_apps(message):
    user_id = message.from_user.id
    apps = load_apps(user_id)
    if apps:
        app_list = '\n'.join([app[0] for app in apps])
        bot.reply_to(message, f"التطبيقات المخزنة الخاصة بك:\n{app_list}")
    else:
        bot.reply_to(message, "لم تقم بتخزين أي تطبيقات حتى الآن.")

# إضافة تطبيق جديد
@bot.message_handler(func=lambda message: message.text == 'إضافة تطبيق')
def add_app(message):
    bot.reply_to(message, "أرسل اسم التطبيق الذي تريد إضافته.")
    bot.register_next_step_handler(message, process_new_app)

def process_new_app(message):
    app_name = message.text
    user_id = message.from_user.id
    save_app(app_name, user_id)
    bot.reply_to(message, f"تمت إضافة التطبيق {app_name} بنجاح.")

# حذف تطبيق
@bot.message_handler(func=lambda message: message.text == 'حذف تطبيق')
def remove_app(message):
    bot.reply_to(message, "أرسل اسم التطبيق الذي تريد حذفه.")
    bot.register_next_step_handler(message, process_remove_app)

def process_remove_app(message):
    app_name = message.text
    delete_app(app_name)
    bot.reply_to(message, f"تم حذف التطبيق {app_name} بنجاح.")

# حساب المستخدم
@bot.message_handler(func=lambda message: message.text == 'حسابي')
def my_account(message):
    user_id = message.from_user.id
    username = message.from_user.username
    save_account(user_id, username)
    bot.reply_to(message, f"تم تسجيل حسابك بنجاح، {username}.")

# التعامل مع الرسائل غير المعروفة
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "لا أفهم رسالتك. يرجى استخدام الأزرار.")

# تشغيل البوت
bot.polling()
