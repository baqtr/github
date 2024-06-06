import os
import json
import logging
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import requests
from datetime import datetime

# إعداد تسجيل الدخول
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# المتغيرات العالمية
user_accounts = {}
backup_file_path = 'backup.json'

# الدوال الأساسية

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("إضافة API", callback_data='add_api')],
        [InlineKeyboardButton("حساباتك", callback_data='show_accounts')],
        [InlineKeyboardButton("حفظ نسخة احتياطية", callback_data='backup_data')],
        [InlineKeyboardButton("استرجاع نسخة احتياطية", callback_data='restore_data')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('مرحبًا! استخدم الأزرار التالية:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'add_api':
        query.edit_message_text(text="الرجاء إرسال مفتاح API الخاص بـ Heroku.")
        return ADD_API
    elif query.data == 'show_accounts':
        show_accounts(update, context)
    elif query.data == 'backup_data':
        backup_data(update, context)
    elif query.data == 'restore_data':
        query.edit_message_text(text="الرجاء إرسال ملف النسخة الاحتياطية (JSON).")

def add_api(update: Update, context: CallbackContext):
    api_key = update.message.text.strip()
    user_id = update.message.from_user.id

    if user_id not in user_accounts:
        user_accounts[user_id] = []

    if api_key in [account['api_key'] for account in user_accounts[user_id]]:
        update.message.reply_text("هذا الحساب مضاف مسبقًا.")
    elif validate_heroku_api_key(api_key):
        user_accounts[user_id].append({'api_key': api_key})
        update.message.reply_text("تمت إضافة حساب Heroku بنجاح!")
    else:
        update.message.reply_text("مفتاح API غير صحيح. يرجى المحاولة مرة أخرى.")

def show_accounts(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    accounts = user_accounts.get(user_id, [])
    if not accounts:
        update.callback_query.edit_message_text("لا توجد حسابات لعرضها.")
    else:
        account_list = "\n".join([f"Account {i+1}: {account['api_key']}" for i, account in enumerate(accounts)])
        update.callback_query.edit_message_text(f"حساباتك:\n{account_list}")

def validate_heroku_api_key(api_key):
    response = requests.get('https://api.heroku.com/account', headers={
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    })
    return response.status_code == 200

def backup_data(update: Update, context: CallbackContext):
    with open(backup_file_path, 'w') as backup_file:
        json.dump(user_accounts, backup_file)
    update.callback_query.edit_message_text("تم حفظ النسخة الاحتياطية بنجاح!")
    context.bot.send_document(chat_id=update.callback_query.message.chat_id, document=open(backup_file_path, 'rb'))

def handle_restore_file(update: Update, context: CallbackContext):
    if update.message.document and update.message.document.mime_type == 'application/json':
        file_info = context.bot.get_file(update.message.document.file_id)
        downloaded_file = file_info.download_as_bytearray()
        backup_content = json.loads(downloaded_file)
        global user_accounts
        user_accounts = backup_content
        update.message.reply_text("تم استرجاع النسخة الاحتياطية بنجاح.")
    else:
        update.message.reply_text("الملف المرسل ليس بملف JSON صالح. يرجى المحاولة مرة أخرى.")

def main():
    # استبدل TOKEN بالرمز الخاص بك
    TOKEN = "7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20"
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, add_api))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/json"), handle_restore_file))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
