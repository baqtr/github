import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7031770762:AAEKh2HzaEn-mUm6YkqGm6qZA2JRJGOUQ20'
bot = telebot.TeleBot(API_TOKEN)

# البيانات للمستخدمين
user_data = {}

# إعداد الوضع الآمن بشكل افتراضي
safe_mode = {
    'enabled': False,
    'prevent_deletion': True,
    'auto_delete_heroku_api': False
}

# وظيفة لإظهار لوحة الأزرار
def show_buttons(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("إضافة API", callback_data="add_api"),
        InlineKeyboardButton("حساباتك", callback_data="view_accounts"),
        InlineKeyboardButton(f"الوضع الآمن: {'مفعل ✅' if safe_mode['enabled'] else 'معطل ❌'}", callback_data="toggle_safe_mode"),
        InlineKeyboardButton("إعدادات الوضع الآمن", callback_data="safe_mode_settings")
    )
    bot.send_message(message.chat.id, "اختر خياراً:", reply_markup=markup)

# دالة البدء
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً! استخدم الأزرار التالية للتفاعل مع البوت.")
    show_buttons(message)

# دالة لإضافة API
@bot.callback_query_handler(func=lambda call: call.data == "add_api")
def add_api(call):
    msg = bot.send_message(call.message.chat.id, "الرجاء إدخال API Heroku:")
    bot.register_next_step_handler(msg, save_api)

def save_api(message):
    user_id = message.from_user.id
    api = message.text
    if user_id not in user_data:
        user_data[user_id] = {'apis': [], 'apps': {}}
    user_data[user_id]['apis'].append(api)
    bot.send_message(message.chat.id, "تم حفظ API بنجاح.")
    show_buttons(message)

# دالة لعرض الحسابات
@bot.callback_query_handler(func=lambda call: call.data == "view_accounts")
def view_accounts(call):
    user_id = call.from_user.id
    if user_id in user_data and user_data[user_id]['apis']:
        markup = InlineKeyboardMarkup()
        for i, api in enumerate(user_data[user_id]['apis']):
            markup.add(InlineKeyboardButton(f"API {i+1}", callback_data=f"manage_api_{i}"))
        markup.add(InlineKeyboardButton("رجوع", callback_data="back"))
        bot.edit_message_text("اختر API لإدارته:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "لا توجد حسابات محفوظة.")
        show_buttons(call.message)

# دالة لإدارة API محدد
@bot.callback_query_handler(func=lambda call: call.data.startswith("manage_api_"))
def manage_api(call):
    user_id = call.from_user.id
    api_index = int(call.data.split("_")[2])
    if user_id in user_data and api_index < len(user_data[user_id]['apis']):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("إنشاء تطبيق", callback_data=f"create_app_{api_index}"),
            InlineKeyboardButton("حذف تطبيق", callback_data=f"delete_app_{api_index}"),
            InlineKeyboardButton("رجوع", callback_data="view_accounts")
        )
        bot.edit_message_text(f"إدارة API {api_index + 1}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

# دالة لإنشاء تطبيق
@bot.callback_query_handler(func=lambda call: call.data.startswith("create_app_"))
def create_app(call):
    api_index = int(call.data.split("_")[2])
    user_id = call.from_user.id
    # إضافة كود لإنشاء تطبيق هنا
    bot.send_message(call.message.chat.id, f"تم إنشاء تطبيق جديد لـ API {api_index + 1}")
    show_buttons(call.message)

# دالة لحذف تطبيق
@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_app_"))
def delete_app(call):
    api_index = int(call.data.split("_")[2])
    user_id = call.from_user.id
    if safe_mode['enabled'] and safe_mode['prevent_deletion']:
        bot.send_message(call.message.chat.id, "لا يمكن حذف التطبيقات بسبب تفعيل الوضع الآمن.")
    else:
        # إضافة كود لحذف تطبيق هنا
        bot.send_message(call.message.chat.id, f"تم حذف تطبيق لـ API {api_index + 1}")
    show_buttons(call.message)

# دالة لتفعيل/تعطيل الوضع الآمن
@bot.callback_query_handler(func=lambda call: call.data == "toggle_safe_mode")
def toggle_safe_mode(call):
    safe_mode['enabled'] = not safe_mode['enabled']
    bot.edit_message_text(f"الوضع الآمن: {'مفعل ✅' if safe_mode['enabled'] else 'معطل ❌'}", call.message.chat.id, call.message.message_id)
    show_buttons(call.message)

# دالة لإعدادات الوضع الآمن
@bot.callback_query_handler(func=lambda call: call.data == "safe_mode_settings")
def safe_mode_settings(call):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(f"منع الحذف: {'مفعل ✅' if safe_mode['prevent_deletion'] else 'معطل ❌'}", callback_data="toggle_prevent_deletion"),
        InlineKeyboardButton(f"حذف تلقائي للـ API: {'مفعل ✅' if safe_mode['auto_delete_heroku_api'] else 'معطل ❌'}", callback_data="toggle_auto_delete_api"),
        InlineKeyboardButton("رجوع", callback_data="back")
    )
    bot.edit_message_text("إعدادات الوضع الآمن:", call.message.chat.id, call.message.message_id, reply_markup=markup)

# دوال لتفعيل/تعطيل إعدادات الوضع الآمن
@bot.callback_query_handler(func=lambda call: call.data == "toggle_prevent_deletion")
def toggle_prevent_deletion(call):
    safe_mode['prevent_deletion'] = not safe_mode['prevent_deletion']
    safe_mode_settings(call)

@bot.callback_query_handler(func=lambda call: call.data == "toggle_auto_delete_api")
def toggle_auto_delete_api(call):
    safe_mode['auto_delete_heroku_api'] = not safe_mode['auto_delete_heroku_api']
    safe_mode_settings(call)

# دالة للعودة إلى القائمة الرئيسية
@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    show_buttons(call.message)

# تشغيل البوت
bot.polling()
