import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import requests

# إعداد تسجيل الدخول
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# المتغيرات العالمية
user_accounts = {}
safe_mode = {}
backup_file_path = 'backup.json'

# الدوال الأساسية

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("إضافة API", callback_data='add_api')],
        [InlineKeyboardButton("حساباتك", callback_data='show_accounts')],
        [InlineKeyboardButton("الوضع الآمن", callback_data='toggle_safe_mode')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('مرحبًا! استخدم الأزرار التالية:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'add_api':
        query.edit_message_text(text="الرجاء إرسال مفتاح API الخاص بـ Heroku.")
    elif query.data == 'show_accounts':
        show_accounts(update, context)
    elif query.data == 'toggle_safe_mode':
        toggle_safe_mode(update, context)

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
        keyboard = [[InlineKeyboardButton(f"Account {i+1}", callback_data=f'account_{i}')] for i in range(len(accounts))]
        keyboard.append([InlineKeyboardButton("رجوع", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text("حساباتك:", reply_markup=reply_markup)

def account_details(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    account_index = int(query.data.split('_')[1])
    account = user_accounts[user_id][account_index]

    keyboard = [
        [InlineKeyboardButton("حذف", callback_data=f'delete_account_{account_index}')],
        [InlineKeyboardButton("إنشاء تطبيق", callback_data=f'create_app_{account_index}')],
        [InlineKeyboardButton("رجوع", callback_data='show_accounts')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(f"API Key: {account['api_key']}\nاختر أحد الخيارات:", reply_markup=reply_markup)

def delete_account(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    account_index = int(query.data.split('_')[2])

    if safe_mode.get(user_id, False):
        query.answer("لا يمكن حذف الحساب أثناء تفعيل الوضع الآمن.")
        return

    del user_accounts[user_id][account_index]
    query.edit_message_text("تم حذف الحساب بنجاح.")
    show_accounts(update, context)

def create_app(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    account_index = int(query.data.split('_')[2])
    api_key = user_accounts[user_id][account_index]['api_key']

    response = requests.post(
        'https://api.heroku.com/apps',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/vnd.heroku+json; version=3'
        }
    )

    if response.status_code == 201:
        app_info = response.json()
        query.edit_message_text(f"تم إنشاء التطبيق بنجاح!\nاسم التطبيق: {app_info['name']}")
    else:
        query.edit_message_text("فشل في إنشاء التطبيق.")

def toggle_safe_mode(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    safe_mode[user_id] = not safe_mode.get(user_id, False)
    status = "مفعل ✅" if safe_mode[user_id] else "معطل ❌"
    update.callback_query.edit_message_text(f"الوضع الآمن: {status}")

def validate_heroku_api_key(api_key):
    response = requests.get('https://api.heroku.com/account', headers={
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    })
    return response.status_code == 200

def main():
    TOKEN = "7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20"
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button, pattern='^((?!account_).)*$'))
    dp.add_handler(CallbackQueryHandler(account_details, pattern='^account_'))
    dp.add_handler(CallbackQueryHandler(delete_account, pattern='^delete_account_'))
    dp.add_handler(CallbackQueryHandler(create_app, pattern='^create_app_'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, add_api))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
