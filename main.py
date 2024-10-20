import logging
import datetime
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from pytz import timezone

# تمكين تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# استبدل 'YOUR_API_KEY' بمفتاح API الخاص بك من OpenWeatherMap
WEATHER_API_KEY = 'YOUR_API_KEY'
# استبدل 'YOUR_TELEGRAM_BOT_TOKEN' بالرمز الخاص بالبوت الذي أنشأته
TELEGRAM_BOT_TOKEN = '7464446606:AAFb6FK5oAwLEiuDCftx2cA2jfSBPsyJjj8'

# دالة لجلب حالة الطقس من OpenWeatherMap
def get_weather():
    city = "Baghdad"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ar"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        weather_desc = data['weather'][0]['description']
        return f"درجة الحرارة: {temp}°C، حالة الطقس: {weather_desc}"
    else:
        return "لم أتمكن من جلب حالة الطقس حالياً."

# دالة لجلب الوقت والتاريخ بتوقيت العراق
def get_time_date():
    iraq_tz = timezone('Asia/Baghdad')
    now = datetime.datetime.now(iraq_tz)
    months_ar = [
        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    ]
    month = months_ar[now.month - 1]
    formatted_time = now.strftime(f"%H:%M:%S")
    formatted_date = now.strftime(f"%d {month} %Y")
    return f"الوقت الآن: {formatted_time}\nالتاريخ: {formatted_date}"

# دالة الرد على الأمر /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('مرحباً! سأقوم بعرض الوقت والتاريخ وحالة الطقس لك باستمرار!')

# دالة تحديث الوقت والتاريخ
def time_and_weather(update: Update, context: CallbackContext) -> None:
    time_date = get_time_date()
    weather = get_weather()
    message = f"{time_date}\n{weather}"
    update.message.reply_text(message)

# دالة رئيسية لبدء البوت
def main():
    # استبدل YOUR_TELEGRAM_BOT_TOKEN برمز البوت
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    # ربط الأوامر بالدوال
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("time", time_and_weather))

    # بدء البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
