import telebot
import requests
import json

API_TOKEN = '7464446606:AAFb6FK5oAwLEiuDCftx2cA2jfSBPsyJjj8'
ADMIN_ID = 7013440973
CHANNEL_URL = "https://t.me/M1telegramM1"
bot = telebot.TeleBot(API_TOKEN)

# قائمة لتخزين معرفات المستخدمين الذين استقبلوا رسالة الاشتراك
subscribed_users = set()
# قائمة لتخزين معرفات المستخدمين
users = {}

# دالة لإرسال رسالة طويلة مقسمة
def send_long_message(chat_id, text):
    max_length = 4096  # حد عدد الأحرف في رسالة تيليجرام
    for i in range(0, len(text), max_length):
        bot.send_message(chat_id, text[i:i+max_length])

# دالة لبدء المحادثة وإرسال رسالة الاشتراك
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id not in subscribed_users:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="اشترك في قناتي", url=CHANNEL_URL)
        markup.add(btn)
        bot.send_message(message.chat.id, "أهلاً بك! يرجى الاشتراك في قناتي.", reply_markup=markup)
        subscribed_users.add(message.from_user.id)
        # إرسال إشعار للأدمن عند دخول مستخدم جديد
        bot.send_message(ADMIN_ID, f"مستخدم جديد دخل البوت: @{message.from_user.username}")
    else:
        bot.send_message(message.chat.id, "أهلاً بك! أرسل لي رابط موقع وسأقوم بإرسال ملف الـ HTML الخاص به.")
    users[message.from_user.id] = message.from_user.username

# دالة لمعالجة الروابط المرسلة
@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_url(message):
    url = message.text
    try:
        response = requests.get(url)
        response.raise_for_status()  # تأكد من أن الطلب ناجح
        html_content = response.text
        # حفظ محتوى HTML في ملف
        with open("website.html", "w", encoding='utf-8') as file:
            file.write(html_content)
        # إرسال الملف للمستخدم
        with open("website.html", "rb") as file:
            bot.send_document(message.chat.id, file)
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"حدث خطأ أثناء تحميل الموقع: {e}")

# دالة لعرض عدد المستخدمين الذين ضغطوا على /start
@bot.message_handler(commands=['sh'])
def show_user_count(message):
    if message.from_user.id == ADMIN_ID:
        user_count = len(users)
        bot.send_message(message.chat.id, f"عدد المستخدمين الذين ضغطوا على /start: {user_count}")

bot.infinity_polling()
