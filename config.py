import os

class Config(object):
    # استدعاء القيم من متغيرات البيئة الصحيحة
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7137946160:AAEtwG3rYA9WwtWCUNsSVxERMPDJVrke-DE")  # توكن البوت
    APP_ID = int(os.environ.get("APP_ID", 7013440973))  # App ID الافتراضي
    API_HASH = os.environ.get("API_HASH", "bcdae25b210b2cbe27c03117328648a2")  # API Hash الافتراضي
