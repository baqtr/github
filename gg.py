import os
import telebot
import requests
import threading
import time
import zipfile
import tempfile
import random
import string
import shutil
from datetime import datetime, timedelta
import pytz
from github import Github
import psycopg2

# استيراد توكن البوت من المتغيرات البيئية
bot_token = os.getenv("BOT_TOKEN", "7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20")
github_token = os.getenv("GITHUB_TOKEN", "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")
database_url = os.getenv("DATABASE_URL", "postgres://u7sp4pi4bkcli5:p8084ef55d7306694913f43fe18ae8f1e24bf9d4c33b1bdae2e9d49737ea39976@ec2-18-210-84-56.compute-1.amazonaws.com:5432/dbdstma1phbk1e")

# إنشاء كائن البوت
bot = telebot.TeleBot(bot_token)

# الهيروكو API
HEROKU_BASE_URL = 'https://api.heroku.com'

# قائمة التطبيقات المجدولة للحذف الذاتي
self_deleting_apps = {}
g = Github(github_token)

# دالة للاتصال بقاعدة البيانات
def get_db_connection():
    return psycopg2.connect(database_url)

# تهيئة قاعدة البيانات
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_accounts (
            user_id BIGINT PRIMARY KEY,
            accounts JSONB
        );
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            event_text TEXT,
            event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

# دالة لإضافة حساب مستخدم جديد
def add_user_account(user_id, accounts):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO user_accounts (user_id, accounts) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET accounts = EXCLUDED.accounts;', (user_id, accounts))
    conn.commit()
    cur.close()
    conn.close()

# دالة لاسترجاع حسابات المستخدم
def get_user_accounts(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT accounts FROM user_accounts WHERE user_id = %s;', (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else []

# دالة لإضافة حدث جديد
def add_event(event_text):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO events (event_text) VALUES (%s);', (event_text,))
    conn.commit()
    cur.close()
    conn.close()

# دالة لاسترجاع الأحداث
def get_events():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT event_text FROM events ORDER BY event_time DESC;')
    result = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in result]

# تهيئة قاعدة البيانات عند بدء تشغيل البرنامج
init_db()

# معالجة الأوامر
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    accounts = get_user_accounts(user_id)
    if not accounts:
        bot.reply_to(message, "مرحباً بك! يبدو أنك مستخدم جديد.")
        add_user_account(user_id, [])
    else:
        bot.reply_to(message, "مرحباً بك مجدداً!")

@bot.message_handler(commands=['addevent'])
def add_event_command(message):
    event_text = message.text[len('/addevent '):]
    if event_text:
        add_event(event_text)
        bot.reply_to(message, "تم إضافة الحدث بنجاح.")
    else:
        bot.reply_to(message, "يرجى كتابة نص الحدث بعد الأمر.")

@bot.message_handler(commands=['events'])
def list_events(message):
    events = get_events()
    if events:
        bot.reply_to(message, "\n".join(events))
    else:
        bot.reply_to(message، "لا توجد أحداث مسجلة.")

# بدء الاستماع للرسائل
bot.polling()
