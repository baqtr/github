import os
import telebot
import requests

# استيراد توكن البوت من المتغيرات البيئية
bot_token = "7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20"

# إنشاء كائن البوت
bot = telebot.TeleBot(bot_token)

# الهيروكو API
HEROKU_BASE_URL = 'https://api.heroku.com'

# قائمة التطبيقات المجدولة للحذف الذاتي
self_deleting_apps = {}

# تخزين حسابات المستخدم
user_accounts = {}

# قائمة لتخزين الأحداث
events = []

# حالة الوضع الآمن لكل مستخدم
safe_mode = {}

# إعدادات الوضع الآمن لكل مستخدم
safe_mode_settings = {}

# دالة لإنشاء الأزرار وتخصيصها
def create_main_buttons(user_id):
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton("إضافة حساب ➕", callback_data="add_account")
    button2 = telebot.types.InlineKeyboardButton("حساباتك 🗂️", callback_data="list_accounts")
    button3 = telebot.types.InlineKeyboardButton("الأحداث 🔄", callback_data="show_events")
    button4 = telebot.types.InlineKeyboardButton("الإعدادات ⚙", callback_data="settings")
    safe_mode_status = "مفعل ✅" if safe_mode.get(user_id, False) else "معطل ❌"
    button5 = telebot.types.InlineKeyboardButton(f"الوضع الآمن: {safe_mode_status}", callback_data="toggle_safe_mode")
    markup.add(button1, button2)
    markup.add(button3)
    markup.add(button4)
    markup.add(button5)
    return markup

def create_account_control_buttons(account_index):
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton("حذف تطبيق ❌", callback_data=f"delete_app_{account_index}")
    button2 = telebot.types.InlineKeyboardButton("إنشاء تطبيق ➕", callback_data=f"create_app_{account_index}")
    markup.add(button1)
    markup.add(button2)
    markup.add(telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="list_accounts"))
    return markup

def create_back_button():
    markup = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="go_back")
    markup.add(back_button)
    return markup

def create_safe_mode_settings_buttons(user_id):
    markup = telebot.types.InlineKeyboardMarkup()
    delete_prevention_status = "مفعل ✅" if safe_mode_settings.get(user_id, {}).get("delete_prevention", False) else "معطل ❌"
    auto_delete_api_status = "مفعل ✅" if safe_mode_settings.get(user_id, {}).get("auto_delete_api", False) else "معطل ❌"
    button1 = telebot.types.InlineKeyboardButton(f"منع الحذف: {delete_prevention_status}", callback_data="toggle_delete_prevention")
    button2 = telebot.types.InlineKeyboardButton(f"حذف API تلقائيًا: {auto_delete_api_status}", callback_data="toggle_auto_delete_api")
    markup.add(button1)
    markup.add(button2)
    markup.add(telebot.types.InlineKeyboardButton("العودة ↩️", callback_data="settings"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in user_accounts:
        user_accounts[user_id] = []
        events.append(f"انضم مستخدم جديد: [{message.from_user.first_name}](tg://user?id={user_id})")
    bot.send_message(message.chat.id, "مرحبًا بك! اضغط على الأزرار أدناه لتنفيذ الإجراءات.", reply_markup=create_main_buttons(user_id))

def add_account(call):
    msg = bot.edit_message_text("يرجى إرسال مفتاح API الخاص بحساب Heroku:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
    bot.register_next_step_handler(msg, handle_new_account)

def handle_new_account(message):
    api_key = message.text.strip()
    user_id = message.from_user.id
    if api_key in [account['api_key'] for account in user_accounts[user_id]]:
        bot.send_message(message.chat.id, "هذا الحساب مضاف مسبقًا.", reply_markup=create_main_buttons(user_id))
    elif validate_heroku_api_key(api_key):
        user_accounts[user_id].append({'api_key': api_key})
        events.append(f"أضاف [{message.from_user.first_name}](tg://user?id={user_id}) حساب جديد: `{api_key[:-4]}****`")
        bot.send_message(message.chat.id, "تمت إضافة حساب Heroku بنجاح!", reply_markup=create_main_buttons(user_id))
    else:
        bot.send_message(message.chat.id, "مفتاح API غير صحيح. يرجى المحاولة مرة أخرى.", reply_markup=create_main_buttons(user_id))

def validate_heroku_api_key(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    response = requests.get(f'{HEROKU_BASE_URL}/apps', headers=headers)
    return response.status_code == 200

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

def get_heroku_account_name(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    response = requests.get(f'{HEROKU_BASE_URL}/account', headers=headers)
    if response.status_code == 200:
        return response.json().get('email', 'Unknown')
    return 'Unknown'

def delete_app(call):
    account_index = int(call.data.split("_")[-1])
    user_id = call.from_user.id
    if safe_mode.get(user_id, False) and safe_mode_settings.get(user_id, {}).get("delete_prevention", False):
        bot.edit_message_text("لا يمكن حذف التطبيق بسبب تفعيل الوضع الآمن.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
    else:
        msg = bot.edit_message_text("يرجى إرسال اسم التطبيق لحذفه:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())
        bot.register_next_step_handler(msg, lambda m: handle_app_name_for_deletion(m, account_index))

def handle_app_name_for_deletion(message, account_index):
    app_name = message.text.strip()
    user_id = message.from_user.id
    headers = {
        'Authorization': f'Bearer {user_accounts[user_id][account_index]["api_key"]}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    response = requests.delete(f'{HEROKU_BASE_URL}/apps/{app_name}', headers=headers)
    if response.status_code == 202:
        events.append(f"حذف [{message.from_user.first_name}](tg://user?id={user_id}) التطبيق: `{app_name[:-2]}**`")
        bot.send_message(message.chat.id, f"تم حذف التطبيق `{app_name}` بنجاح.", reply_markup=create_main_buttons(user_id), parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, f"حدث خطأ أثناء محاولة حذف التطبيق `{app_name}`. يرجى المحاولة مرة أخرى.", reply_markup=create_main_buttons(user_id), parse_mode='Markdown')

def create_app(call):
    account_index = int(call.data.split("_")[-1])
    user_id = call.from_user.id
    api_key = user_accounts[user_id][account_index]["api_key"]
    app_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    response = requests.post(f'{HEROKU_BASE_URL}/apps', headers=headers, json={"name": app_name})
    if response.status_code == 201:
        events.append(f"أنشأ [{call.from_user.first_name}](tg://user?id={user_id}) تطبيق جديد: `{app_name}`")
        bot.edit_message_text(f"تم إنشاء التطبيق `{app_name}` بنجاح.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_main_buttons(user_id), parse_mode='Markdown')
    else:
        bot.edit_message_text(f"حدث خطأ أثناء محاولة إنشاء التطبيق. يرجى المحاولة مرة أخرى.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_main_buttons(user_id), parse_mode='Markdown')

def toggle_safe_mode(call):
    user_id = call.from_user.id
    safe_mode[user_id] = not safe_mode.get(user_id, False)
    status = "مفعل ✅" if safe_mode[user_id] else "معطل ❌"
    bot.edit_message_text(f"الوضع الآمن: {status}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_main_buttons(user_id))

def settings(call):
    user_id = call.from_user.id
    bot.edit_message_text("إعدادات الوضع الآمن:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_safe_mode_settings_buttons(user_id))

def toggle_delete_prevention(call):
    user_id = call.from_user.id
    settings = safe_mode_settings.setdefault(user_id, {})
    settings["delete_prevention"] = not settings.get("delete_prevention", False)
    bot.edit_message_text("إعدادات الوضع الآمن:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_safe_mode_settings_buttons(user_id))

def toggle_auto_delete_api(call):
    user_id = call.from_user.id
    settings = safe_mode_settings.setdefault(user_id, {})
    settings["auto_delete_api"] = not settings.get("auto_delete_api", False)
    bot.edit_message_text("إعدادات الوضع الآمن:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_safe_mode_settings_buttons(user_id))

def show_events(call):
    if events:
        events_list = "\n".join(events)
        bot.edit_message_text(f"الأحداث الأخيرة:\n{events_list}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button(), parse_mode='Markdown')
    else:
        bot.edit_message_text("لا توجد أحداث.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_back_button())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "add_account":
        add_account(call)
    elif call.data == "list_accounts":
        list_accounts(call)
    elif call.data == "show_events":
        show_events(call)
    elif call.data == "settings":
        settings(call)
    elif call.data == "toggle_safe_mode":
        toggle_safe_mode(call)
    elif call.data == "toggle_delete_prevention":
        toggle_delete_prevention(call)
    elif call.data == "toggle_auto_delete_api":
        toggle_auto_delete_api(call)
    elif call.data.startswith("select_account_"):
        account_index = int(call.data.split("_")[-1])
        bot.edit_message_text(f"التحكم في الحساب {account_index + 1}:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_account_control_buttons(account_index))
    elif call.data.startswith("delete_app_"):
        delete_app(call)
    elif call.data.startswith("create_app_"):
        create_app(call)
    elif call.data == "go_back":
        bot.edit_message_text("مرحبًا بك! اضغط على الأزرار أدناه لتنفيذ الإجراءات.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_main_buttons(call.from_user.id))

bot.polling()
