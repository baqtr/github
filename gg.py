import telebot
import os
import psycopg2
from telebot import types
from datetime import datetime, timedelta

TOKEN = '7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20'
database_url = os.getenv("DATABASE_URL", "postgres://u7sp4pi4bkcli5:p8084ef55d7306694913f43fe18ae8f1e24bf9d4c33b1bdae2e9d49737ea39976@ec2-18-210-84-56.compute-1.amazonaws.com:5432/dbdstma1phbk1e")

bot = telebot.TeleBot(TOKEN)

# إعداد قاعدة البيانات
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        api_key TEXT,
        application_name TEXT,
        delete_at TIMESTAMP
    )
''')
conn.commit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('إضافة حساب')
    btn2 = types.KeyboardButton('حساباتك')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "مرحباً! اختر إجراءً:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'إضافة حساب')
def add_account(message):
    msg = bot.send_message(message.chat.id, "أرسل مفتاح API الخاص بك:")
    bot.register_next_step_handler(msg, receive_api_key)

def receive_api_key(message):
    user_id = message.from_user.id
    api_key = message.text
    # تحقق من صحة API (يمكنك إضافة التحقق من خلال استدعاء API هنا)
    msg = bot.send_message(message.chat.id, "أرسل اسم التطبيق:")
    bot.register_next_step_handler(msg, receive_application_name, api_key)

def receive_application_name(message, api_key):
    user_id = message.from_user.id
    application_name = message.text
    cursor.execute("INSERT INTO accounts (user_id, api_key, application_name) VALUES (%s, %s, %s)", (user_id, api_key, application_name))
    conn.commit()
    bot.send_message(message.chat.id, "تمت إضافة الحساب بنجاح!")

@bot.message_handler(func=lambda message: message.text == 'حساباتك')
def show_accounts(message):
    user_id = message.from_user.id
    cursor.execute("SELECT id, application_name FROM accounts WHERE user_id = %s", (user_id,))
    accounts = cursor.fetchall()
    if accounts:
        markup = types.InlineKeyboardMarkup()
        for account in accounts:
            btn = types.InlineKeyboardButton(account[1], callback_data=f"account_{account[0]}")
            markup.add(btn)
        bot.send_message(message.chat.id, "اختر حساباً للتحكم:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "لا توجد حسابات مضافة.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('account_'))
def account_options(call):
    account_id = call.data.split('_')[1]
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('حذف ذاتي')
    btn2 = types.KeyboardButton('عرض التطبيقات')
    btn3 = types.KeyboardButton('عرض الوقت المتبقي للحذف الذاتي')
    markup.add(btn1, btn2, btn3)
    bot.send_message(call.message.chat.id, "اختر إجراءً:", reply_markup=markup)
    bot.register_next_step_handler(call.message, account_action, account_id)

def account_action(message, account_id):
    if message.text == 'حذف ذاتي':
        msg = bot.send_message(message.chat.id, "أرسل اسم التطبيق:")
        bot.register_next_step_handler(msg, set_auto_delete, account_id)
    elif message.text == 'عرض التطبيقات':
        show_apps(message, account_id)
    elif message.text == 'عرض الوقت المتبقي للحذف الذاتي':
        show_remaining_time(message, account_id)

def set_auto_delete(message, account_id):
    application_name = message.text
    msg = bot.send_message(message.chat.id, "أرسل الوقت المراد للحذف (بالدقائق):")
    bot.register_next_step_handler(msg, confirm_auto_delete, account_id, application_name)

def confirm_auto_delete(message, account_id, application_name):
    try:
        minutes = int(message.text)
        delete_at = datetime.utcnow() + timedelta(minutes=minutes)
        cursor.execute("UPDATE accounts SET delete_at = %s WHERE id = %s AND application_name = %s", (delete_at, account_id, application_name))
        conn.commit()
        bot.send_message(message.chat.id, f"سيتم حذف التطبيق '{application_name}' بعد {minutes} دقيقة.")
    except ValueError:
        bot.send_message(message.chat.id, "الرجاء إدخال عدد صحيح للدقائق.")

def show_apps(message, account_id):
    cursor.execute("SELECT application_name FROM accounts WHERE id = %s", (account_id,))
    apps = cursor.fetchall()
    if apps:
        response = '\n'.join([app[0] for app in apps])
    else:
        response = "لا توجد تطبيقات مضافة."
    bot.send_message(message.chat.id, response)

def show_remaining_time(message, account_id):
    cursor.execute("SELECT application_name, delete_at FROM accounts WHERE id = %s AND delete_at IS NOT NULL", (account_id,))
    apps = cursor.fetchall()
    if apps:
        response = ''
        for app in apps:
            remaining_time = app[1] - datetime.utcnow()
            response += f"التطبيق: {app[0]}، الوقت المتبقي: {remaining_time}\n"
    else:
        response = "لا توجد تطبيقات مجدولة للحذف."
    bot.send_message(message.chat.id, response)

if __name__ == '__main__':
    bot.polling()
