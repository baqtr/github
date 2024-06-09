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

# دالة لإنشاء جدول الصور إذا لم يكن موجودًا
def create_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS stickers (
                        id SERIAL PRIMARY KEY,
                        file_id TEXT,
                        emoji TEXT
                      );''')
    connection.commit()

create_table()

# دالة لحفظ الملصق في قاعدة البيانات
def save_sticker(file_id, emoji):
    cursor.execute('''INSERT INTO stickers (file_id, emoji)
                      VALUES (%s, %s);''', (file_id, emoji))
    connection.commit()

# دالة لجلب الملصقات من قاعدة البيانات
def load_stickers():
    cursor.execute("SELECT * FROM stickers")
    return cursor.fetchall()

# عرض القائمة الرئيسية
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_button = types.KeyboardButton('إضافة ملصق')
    view_button = types.KeyboardButton('عرض الملصقات')
    markup.add(add_button, view_button)
    return markup

# إضافة ملصق جديد
@bot.message_handler(func=lambda message: message.text == 'إضافة ملصق')
def add_sticker(message):
    bot.reply_to(message, "قم بإرسال الملصق.")
    bot.register_next_step_handler(message, process_new_sticker)

def process_new_sticker(message):
    file_id = message.sticker.file_id
    emoji = message.sticker.emoji
    save_sticker(file_id, emoji)
    bot.reply_to(message, "تم حفظ الملصق بنجاح.")

# عرض الملصقات المخزنة
@bot.message_handler(func=lambda message: message.text == 'عرض الملصقات')
def show_stickers(message):
    stickers = load_stickers()
    if stickers:
        bot.send_message(message.chat.id, "الملصقات المخزنة:")
        for sticker in stickers:
            bot.send_sticker(message.chat.id, sticker[1], sticker[2])
    else:
        bot.reply_to(message, "لا توجد ملصقات مخزنة.")

# التعامل مع الرسائل غير المعروفة
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "يرجى استخدام الأزرار.")

# تشغيل البوت
bot.polling()
