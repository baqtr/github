import os
import telebot
import psycopg2
from urllib.parse import urlparse

# إعداد توكن البوت ومعلومات قاعدة البيانات
bot_token = "7031770762:AAF-BrYHNEcX8VyGBzY1mastEG3SWod4_uI"
database_url = os.getenv("DATABASE_URL", "postgres://u7sp4pi4bkcli5:p8084ef55d7306694913f43fe18ae8f1e24bf9d4c33b1bdae2e9d49737ea39976@ec2-18-210-84-56.compute-1.amazonaws.com:5432/dbdstma1phbk1e")


bot = telebot.TeleBot(bot_token)

# إعداد قاعدة البيانات
url = urlparse(DATABASE_URL)
db_conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
db_cursor = db_conn.cursor()

db_cursor.execute("""
CREATE TABLE IF NOT EXISTS stickers (
    user_id BIGINT,
    file_id TEXT,
    set_name TEXT
)
""")
db_conn.commit()

# إنشاء لوحة المفاتيح
def create_keyboard(buttons):
    markup = telebot.types.InlineKeyboardMarkup()
    for button_row in buttons:
        markup.row(*[telebot.types.InlineKeyboardButton(text, callback_data=data) for text, data in button_row])
    return markup

# أمر البدء
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "أهلاً بك في بوت تخزين الملصقات! استخدم الأزرار أدناه لإضافة وعرض الملصقات.",
        reply_markup=create_keyboard([
            [("إضافة ملصق ➕", "add_sticker")],
            [("عرض ملصقاتك 📂", "list_stickers")]
        ])
    )

# إضافة ملصق
@bot.callback_query_handler(func=lambda call: call.data == "add_sticker")
def add_sticker(call):
    msg = bot.edit_message_text("أرسل الملصق الذي تريد تخزينه:", chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.register_next_step_handler(msg, receive_sticker)

def receive_sticker(message):
    if message.sticker:
        user_id = message.from_user.id
        file_id = message.sticker.file_id
        set_name = message.sticker.set_name if message.sticker.set_name else "default"

        db_cursor.execute("INSERT INTO stickers (user_id, file_id, set_name) VALUES (%s, %s, %s)", (user_id, file_id, set_name))
        db_conn.commit()

        bot.send_message(message.chat.id, "تم تخزين الملصق بنجاح!")
    else:
        bot.send_message(message.chat.id, "الرجاء إرسال ملصق صحيح.")

# عرض الملصقات
@bot.callback_query_handler(func=lambda call: call.data == "list_stickers")
def list_stickers(call):
    user_id = call.from_user.id
    db_cursor.execute("SELECT file_id, set_name FROM stickers WHERE user_id = %s", (user_id,))
    stickers = db_cursor.fetchall()

    if stickers:
        for sticker in stickers:
            bot.send_sticker(call.message.chat.id, sticker[0])
    else:
        bot.send_message(call.message.chat.id, "لم تقم بتخزين أي ملصقات بعد.")

# بدء البوت
bot.polling()
