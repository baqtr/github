import telebot
from telebot import types
import requests
import threading
import time
import pytz
from datetime import datetime, timedelta
from github import Github

# تعريف التوكن الخاص بالبوت
API_TOKEN = '7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20'
HEROKU_BASE_URL = 'https://api.heroku.com'
GITHUB_ACCESS_TOKEN = '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'

bot = telebot.TeleBot(API_TOKEN)
g = Github(GITHUB_ACCESS_TOKEN)

user_accounts = {}  # تخزين حسابات المستخدمين
self_deleting_apps = {}  # تخزين التطبيقات المجدولة للحذف الذاتي

# دالة لإنشاء الأزرار الرئيسية
def create_main_buttons():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("حساباتك", callback_data="show_accounts"))
    markup.add(types.InlineKeyboardButton("إضافة حساب", callback_data="add_account"))
    return markup

# دالة لإنشاء زر الرجوع
def create_back_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("رجوع", callback_data="main_menu"))
    return markup

# دالة لمعالجة الأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "main_menu":
        bot.edit_message_text("اهلا وسهلا نورتنا اختار من بين الازرار ماذا تريد", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_main_buttons())
    elif call.data == "show_accounts":
        show_accounts(call)
    elif call.data == "add_account":
        msg = bot.send_message(call.message.chat.id, "يرجى إرسال البريد الإلكتروني وكلمة المرور لحساب Heroku (تنسيق: email:password):", reply_markup=create_back_button())
        bot.register_next_step_handler(msg, handle_add_account)

# دالة لعرض حسابات المستخدم
def show_accounts(call):
    user_id = call.from_user.id
    if user_id not in user_accounts or not user_accounts[user_id]:
        bot.edit_message_text("لا توجد حسابات مضافة.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
        return

    accounts = user_accounts[user_id]
    accounts_text = "\n".join([f"{idx + 1}. {acc['email']}" for idx, acc in enumerate(accounts)])
    bot.edit_message_text(f"حساباتك المضافة:\n{accounts_text}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

# دالة لمعالجة إضافة حساب
def handle_add_account(message):
    try:
        email, password = message.text.strip().split(':')
    except ValueError:
        bot.send_message(message.chat.id, "تنسيق غير صالح. يرجى المحاولة مرة أخرى.", reply_markup=create_main_buttons())
        return

    user_id = message.from_user.id
    if user_id not in user_accounts:
        user_accounts[user_id] = []

    user_accounts[user_id].append({'email': email, 'password': password, 'api_key': get_heroku_api_key(email, password)})
    bot.send_message(message.chat.id, "تم إضافة الحساب بنجاح.", reply_markup=create_main_buttons())

# دالة للحصول على API Key من Heroku
def get_heroku_api_key(email, password):
    response = requests.post('https://api.heroku.com/oauth/authorizations', auth=(email, password), headers={'Accept': 'application/vnd.heroku+json; version=3'})
    if response.status_code == 201:
        return response.json()['access_token']['token']
    else:
        return None

# دالة لمعالجة نشر المستودع
def handle_publish_repo(message):
    repo_name = message.text.strip()
    user_id = message.from_user.id

    if not user_accounts[user_id]:
        bot.send_message(message.chat.id, "لا توجد حسابات مضافة. يرجى إضافة حساب أولاً.", reply_markup=create_main_buttons())
        return

    account = user_accounts[user_id][0]  # اختيار أول حساب للمستخدم
    api_key = account['api_key']

    # تحقق من صحة المستودع على GitHub
    try:
        repo = g.get_repo(repo_name)
    except:
        bot.send_message(message.chat.id, "اسم المستودع غير صحيح. يرجى المحاولة مرة أخرى.", reply_markup=create_main_buttons())
        return

    # مؤقت لنشر المستودع
    msg = bot.send_message(message.chat.id, "جاري رفع المستودع... ⬛⬜ 0%", reply_markup=create_back_button())
    time.sleep(2)

    # إنشاء تطبيق جديد على Heroku
    app_name = repo_name.split('/')[-1]  # استخدام اسم المستودع كاسم التطبيق
    response = create_heroku_app(api_key, app_name)
    if response.status_code != 201:
        bot.send_message(message.chat.id, f"فشل إنشاء تطبيق Heroku. رمز الاستجابة: {response.status_code}", reply_markup=create_main_buttons())
        return

    bot.edit_message_text("جاري رفع المستودع... ⬛⬛ 50%", chat_id=message.chat.id, message_id=msg.message_id)
    time.sleep(2)

    # نشر المستودع على Heroku
    deploy_response = deploy_to_heroku(api_key, app_name, repo.clone_url)
    if deploy_response.status_code != 201:
        bot.send_message(message.chat.id, f"فشل نشر المستودع على Heroku. رمز الاستجابة: {deploy_response.status_code}", reply_markup=create_main_buttons())
        return

    bot.edit_message_text(f"تم نشر المستودع `{repo_name}` بنجاح على Heroku!", chat_id=message.chat.id, message_id=msg.message_id, reply_markup=create_main_buttons(), parse_mode='Markdown')

    # طلب عدد الدينامو
    msg = bot.send_message(message.chat.id, "يرجى إرسال عدد الدينامو للتطبيق المنشور:", reply_markup=create_back_button())
    bot.register_next_step_handler(msg, handle_set_dynos, api_key, app_name)

# دالة لإنشاء تطبيق Heroku
def create_heroku_app(api_key, app_name):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3',
        'Content-Type': 'application/json'
    }
    data = {
        'name': app_name,
        'region': 'us'
    }
    response = requests.post(f'{HEROKU_BASE_URL}/apps', headers=headers, json=data)
    return response

# دالة لنشر المستودع على Heroku
def deploy_to_heroku(api_key, app_name, repo_url):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3',
        'Content-Type': 'application/json'
    }
    data = {
        'source_blob': {
            'url': repo_url
        }
    }
    response = requests.post(f'{HEROKU_BASE_URL}/apps/{app_name}/builds', headers=headers, json=data)
    return response

# دالة لمعالجة عدد الدينامو
def handle_set_dynos(message, api_key, app_name):
    try:
        dyno_count = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "تنسيق غير صالح. يرجى المحاولة مرة أخرى.", reply_markup=create_main_buttons())
        return

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3',
        'Content-Type': 'application/json'
    }
    data = {
        'quantity': dyno_count,
        'size': 'Standard-1X'
    }
    response = requests.patch(f'{HEROKU_BASE_URL}/apps/{app_name}/formation/web', headers=headers, json=data)
    if response.status_code == 200:
        bot.send_message(message.chat.id, f"تم ضبط عدد الدينامو للتطبيق `{app_name}` بنجاح.", reply_markup=create_main_buttons())
    else:
        bot.send_message(message.chat.id, f"فشل ضبط عدد الدينامو. رمز الاستجابة: {response.status_code}", reply_markup=create_main_buttons())

# بدء تشغيل البوت
bot.polling()
