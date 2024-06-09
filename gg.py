import telebot
import os
import psycopg2
from telebot import types

# يجب تغيير هذا إلى TOKEN الخاص بك
TOKEN = '7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20'
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://u7sp4pi4bkcli5:p8084ef55d7306694913f43fe18ae8f1e24bf9d4c33b1bdae2e9d49737ea39976@ec2-18-210-84-56.compute-1.amazonaws.com:5432/dbdstma1phbk1e")

bot = telebot.TeleBot(TOKEN)

# إعداد قاعدة البيانات
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS texts (id SERIAL PRIMARY KEY, user_id BIGINT, text TEXT)''')
conn.commit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('إضافة نص')
    btn2 = types.KeyboardButton('عرض النصوص')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "مرحباً! اختر إجراءً:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'إضافة نص')
def add_text(message):
    msg = bot.send_message(message.chat.id, "أرسل النص لإضافته:")
    bot.register_next_step_handler(msg, save_text)

def save_text(message):
    user_id = message.from_user.id
    text = message.text
    cursor.execute("INSERT INTO texts (user_id, text) VALUES (%s, %s)", (user_id, text))
    conn.commit()
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('إضافة نص')
    btn2 = types.KeyboardButton('عرض النصوص')
    btn_back = types.KeyboardButton('رجوع')
    markup.add(btn1, btn2, btn_back)
    bot.send_message(message.chat.id, "تمت إضافة النص بنجاح!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'عرض النصوص')
def show_texts(message):
    user_id = message.from_user.id
    cursor.execute("SELECT text FROM texts WHERE user_id = %s", (user_id,))
    texts = cursor.fetchall()
    if texts:
        response = '\n'.join([text[0] for text in texts])
    else:
        response = "لا يوجد نصوص محفوظة."
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('إضافة نص')
    btn2 = types.KeyboardButton('عرض النصوص')
    btn_back = types.KeyboardButton('رجوع')
    markup.add(btn1, btn2, btn_back)
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'رجوع')
def go_back(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('إضافة نص')
    btn2 = types.KeyboardButton('عرض النصوص')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "مرحباً! اختر إجراءً:", reply_markup=markup)

if __name__ == '__main__':
    bot.polling()
