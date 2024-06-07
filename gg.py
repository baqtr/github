import os
import telebot
import requests
from github import Github

# استيراد توكن البوت من المتغيرات البيئية
bot_token = "7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20"
github_token = "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"
# إنشاء كائن البوت
bot = telebot.TeleBot(bot_token)

# الهيروكو API
HEROKU_BASE_URL = 'https://api.heroku.com'

# تخزين حسابات المستخدم
user_accounts = {}

# دالة لإنشاء الأزرار وتخصيصها
def create_main_buttons():
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton("إضافة حساب ➕", callback_data="add_account")
    button2 = telebot.types.InlineKeyboardButton("حساباتك 🗂️", callback_data="list_accounts")
    button3 = telebot.types.InlineKeyboardButton("نشر مستودع جيتهاب 🚀", callback_data="deploy_github_repo")
    markup.add(button1, button2, button3)
    return markup

# دالة لإنشاء زر العودة
def create_back_button():
    markup = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="go_back")
    markup.add(back_button)
    return markup

# دالة لإضافة حساب جديد
def add_account(call):
    msg = bot.edit_message_text("يرجى إرسال مفتاح API الخاص بحساب Heroku:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
    bot.register_next_step_handler(msg, handle_new_account)

def handle_new_account(message):
    api_key = message.text.strip()
    user_id = message.from_user.id
    if api_key in [account['api_key'] for account in user_accounts[user_id]]:
        bot.send_message(message.chat.id, "هذا الحساب مضاف مسبقًا.", reply_markup=create_main_buttons())
    elif validate_heroku_api_key(api_key):
        user_accounts[user_id].append({'api_key': api_key})
        bot.send_message(message.chat.id, "تمت إضافة حساب Heroku بنجاح!", reply_markup=create_main_buttons())
    else:
        bot.send_message(message.chat.id, "مفتاح API غير صحيح. يرجى المحاولة مرة أخرى.", reply_markup=create_main_buttons())

# التحقق من صحة مفتاح API
def validate_heroku_api_key(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    response = requests.get(f'{HEROKU_BASE_URL}/apps', headers=headers)
    return response.status_code == 200

# عرض حسابات المستخدم
def list_accounts(call):
    user_id = call.from_user.id
    if user_id in user_accounts and user_accounts[user_id]:
        accounts_list = "\n".join([f"حساب {index + 1}: `{get_heroku_account_name(account['api_key'])}`" for index, account in enumerate(user_accounts[user_id])])
        markup = telebot.types.InlineKeyboardMarkup()
        for index in range(len(user_accounts[user_id])):
            account_name = get_heroku_account_name(user_accounts[user_id][index]['api_key'])
            markup.add(telebot.types.InlineKeyboardButton(f"{account_name}", callback_data=f"select_account_{index}"))
        markup.add(telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="go_back"))
        bot.edit_message_text(f"حساباتك:\n{accounts_list}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.edit_message_text("لا توجد حسابات مضافة.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

# جلب اسم حساب هيروكو
def get_heroku_account_name(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    response = requests.get(f'{HEROKU_BASE_URL}/account', headers=headers)
    if response.status_code == 200:
        return response.json().get('email', 'Unknown')
    return 'Unknown'

# دالة لنشر مستودع جيتهاب على هيروكو
def deploy_github_repo(call):
    msg = bot.edit_message_text("يرجى إرسال رابط مستودع GitHub الخاص بك:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
    bot.register_next_step_handler(msg, handle_github_repo)

def handle_github_repo(message):
    repo_url = message.text.strip()
    user_id = message.from_user.id
    if user_id not in user_accounts or not user_accounts[user_id]:
        bot.send_message(message.chat.id, "يرجى إضافة حساب Heroku أولاً.", reply_markup=create_main_buttons())
        return
    api_key = user_accounts[user_id][0]['api_key']  # افتراضياً نستخدم أول حساب Heroku
    if validate_github_repo(repo_url):
        bot.send_message(message.chat.id, "تم التحقق من صحة رابط المستودع.", reply_markup=create_main_buttons())
        deploy_to_heroku(message.chat.id, api_key, repo_url)
    else:
        bot.send_message(message.chat.id, "رابط المستودع غير صحيح. يرجى المحاولة مرة أخرى.", reply_markup=create_main_buttons())

# التحقق من صحة رابط المستودع في جيتهاب
def validate_github_repo(repo_url):
    try:
        Github(github_token).get_repo(repo_url)
        return True
    except:
        return False

# دالة لنشر المستودع على هيروكو
def deploy_to_heroku(chat_id, api_key, repo_url):
    msg = bot.send_message(chat_id, "يرجى إدخال اسم المستودع للنشر:")
    bot.register_next_step_handler(msg, lambda m: deploy_repo_to_heroku(chat_id, api_key, repo_url, m.text.strip()))

def deploy_repo_to_heroku(chat_id, api_key, repo_url, repo_name):
    heroku_app_name = generate_random_name()
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3',
        'Content-Type': 'application/json'
    }
    data = {
        'name': heroku_app_name,
        'region': 'us'
    }
    response = requests.post(f'{HEROKU_BASE_URL}/apps', headers=headers, json=data)
    if response.status_code == 201:
        app_id = response.json().get('id')
        deploy_status_msg = bot.send_message(chat_id, "جارٍ إنشاء التطبيق على Heroku...")
        deploy_to_heroku_status(chat_id, api_key, repo_url, repo_name, app_id, deploy_status_msg)
    else:
        bot.send_message(chat_id, "حدث خطأ أثناء إنشاء التطبيق على Heroku. يرجى المحاولة مرة أخرى.")

def deploy_to_heroku_status(chat_id, api_key, repo_url, repo_name, app_id, deploy_status_msg):
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/vnd.heroku+json; version=3'
        }
        response = requests.get(f'{HEROKU_BASE_URL}/apps/{app_id}/builds', headers=headers)
        if response.status_code == 200:
            build_status = response.json().get('status')
            if build_status == 'pending':
                bot.edit_message_text("جارٍ النشر...", chat_id=chat_id, message_id=deploy_status_msg.message_id)
                threading.Timer(10, deploy_to_heroku_status, args=[chat_id, api_key, repo_url, repo_name, app_id, deploy_status_msg]).start()
            elif build_status == 'succeeded':
                dyno_count_msg = bot.send_message(chat_id, "يرجى إدخال عدد الدينامو:")
                bot.register_next_step_handler(dyno_count_msg, lambda m: complete_deployment(chat_id, api_key, repo_url, repo_name, app_id, m.text.strip()))
            else:
                bot.send_message(chat_id, "حدث خطأ أثناء عملية النشر. يرجى المحاولة مرة أخرى.")
        else:
            bot.send_message(chat_id, "حدث خطأ أثناء الاستعلام عن حالة النشر على Heroku. يرجى المحاولة مرة أخرى.")
    except Exception as e:
        print(e)
        bot.send_message(chat_id, "حدث خطأ أثناء عملية النشر. يرجى المحاولة مرة أخرى.")

def complete_deployment(chat_id, api_key, repo_url, repo_name, app_id, dyno_count):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3',
        'Content-Type': 'application/json'
    }
    data = {
        'source_blob': {
            'url': f'https://api.github.com/repos/{repo_url}/tarball',
            'version': repo_name
        },
        'app': app_id,
        'buildpacks': [{'url': 'heroku/python'}],
        'formation': {
            'web': {
                'quantity': int(dyno_count),
                'size': 'free'
            }
        }
    }
    response = requests.post(f'{HEROKU_BASE_URL}/apps/{app_id}/builds', headers=headers, json=data)
    if response.status_code == 201:
        bot.send_message(chat_id, "تمت عملية النشر بنجاح!")
    else:
        bot.send_message(chat_id, "حدث خطأ أثناء عملية النشر. يرجى المحاولة مرة أخرى.")

# دالة لإنشاء اسم عشوائي للتطبيق على Heroku
def generate_random_name():
    return ''.join(random.choices(string.ascii_lowercase, k=10))

# دالة للتحقق من وجود اسم المستودع في جيتهاب
def validate_github_repo(repo_url):
    try:
        Github(github_token).get_repo(repo_url)
        return True
    except:
        return False

# دالة لتشغيل البوت
bot.polling() 
