import os
import telebot
import requests
import zipfile
import tempfile
import shutil
import random
import string
from github import Github
from telebot import types

# استيراد توكن البوت من المتغيرات البيئية
bot_token = "6444148337:AAEcKzMdqFprlQmKhp_J598JonchHXvj-hk"
github_token = "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"

# إنشاء كائن البوت
bot = telebot.TeleBot(bot_token)
g = Github(github_token)

# قائمة لتخزين الأحداث والمستخدمين وحالة الإشعارات لكل مستخدم
events = []
users = set()
user_notifications = {}

# دالة لإنشاء الأزرار وتخصيصها
def create_main_buttons(user_id):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("رفع ملف 📤", callback_data="upload_file")
    button2 = types.InlineKeyboardButton("عرض المستودعات 📂", callback_data="list_github_repos")
    button3 = types.InlineKeyboardButton("حذف مستودع 🗑️", callback_data="delete_repo")
    button4 = types.InlineKeyboardButton("حذف الكل 🗑️", callback_data="delete_all_repos")
    button5 = types.InlineKeyboardButton("الأحداث 🔄", callback_data="show_events")
    notification_status = "تفعيل ✅" if user_notifications.get(user_id, True) else "معطل ❌"
    button6 = types.InlineKeyboardButton(f"الإشعارات: {notification_status}", callback_data="toggle_notifications")
    button7 = types.InlineKeyboardButton(f"عدد المستخدمين 👥: {len(users)}", callback_data="user_count")
    markup.row(button1, button2)
    markup.row(button3, button4)
    markup.row(button5)
    markup.row(button6)
    markup.row(button7)
    return markup

# دالة لإنشاء زر العودة
def create_back_button():
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("العودة ↩️", callback_data="go_back")
    markup.add(back_button)
    return markup

# دالة لمعالجة الطلبات الواردة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    users.add(message.chat.id)
    user_notifications[message.chat.id] = True
    bot.send_message(message.chat.id, "مرحبًا بك! اضغط على الأزرار أدناه لتنفيذ الإجراءات.", reply_markup=create_main_buttons(message.chat.id))

# دالة لمعالجة النقرات على الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.message.chat.id
    if call.data == "upload_file":
        msg = bot.send_message(user_id, "يرجى إرسال ملف مضغوط بصيغة ZIP.")
        bot.register_next_step_handler(msg, handle_zip_file)
    elif call.data == "list_github_repos":
        list_github_repos(call)
    elif call.data == "delete_repo":
        msg = bot.send_message(user_id, "يرجى إرسال اسم المستودع لحذفه.")
        bot.register_next_step_handler(msg, handle_repo_deletion)
    elif call.data == "delete_all_repos":
        delete_all_repos(call)
    elif call.data == "show_events":
        show_events(call)
    elif call.data == "toggle_notifications":
        user_notifications[user_id] = not user_notifications.get(user_id, True)
        bot.edit_message_text("تم تعديل حالة الإشعارات.", chat_id=user_id, message_id=call.message.message_id, reply_markup=create_main_buttons(user_id))
    elif call.data == "user_count":
        bot.answer_callback_query(call.id, f"عدد المستخدمين الكلي: {len(users)}")
    elif call.data == "go_back":
        bot.edit_message_text("مرحبًا بك! اضغط على الأزرار أدناه لتنفيذ الإجراءات.", chat_id=user_id, message_id=call.message.message_id, reply_markup=create_main_buttons(user_id))

# دالة لمعالجة ملف ZIP
def handle_zip_file(message):
    if message.document and message.document.mime_type == 'application/zip':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, message.document.file_name)
            with open(zip_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                repo_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                user = g.get_user()
                repo = user.create_repo(repo_name, private=True)
                
                for root, dirs, files in os.walk(temp_dir):
                    for file_name in files:
                        file_path = os.path.join(root, file_name)
                        relative_path = os.path.relpath(file_path, temp_dir)
                        with open(file_path, 'rb') as file_data:
                            repo.create_file(relative_path, f"Add {relative_path}", file_data.read())
                
                num_files = sum([len(files) for r, d, files in os.walk(temp_dir)])
                username = message.from_user.username
                user_link = f"[{username}](https://t.me/{username})"
                event = f"👤 *المستخدم*: {user_link}\n📦 *تم إنشاء المستودع*: `{repo_name}`\n📁 *عدد الملفات*: {num_files}"
                events.append(event)
                bot.send_message(message.chat.id, event, parse_mode='Markdown')
                if user_notifications.get(message.chat.id, True):
                    notify_all_users(event)
    else:
        bot.send_message(message.chat.id, "الملف الذي تم إرساله ليس ملف ZIP. يرجى المحاولة مرة أخرى.")

# دالة لعرض مستودعات GitHub
def list_github_repos(call):
    user = g.get_user()
    repos = user.get_repos()
    repo_list = ""
    loading_message = bot.send_message(call.message.chat.id, "جارٍ جلب المستودعات، يرجى الانتظار...")

    for repo in repos:
        try:
            contents = repo.get_contents("")
            num_files = sum(1 for _ in contents)
            repo_list += f"📂 *اسم المستودع*: `{repo.name}`\n📁 *عدد الملفات*: {num_files}\n\n"
        except:
            pass

    if repo_list:
        bot.edit_message_text(f"مستودعات GitHub:\n{repo_list}", chat_id=call.message.chat.id, message_id=loading_message.message_id, parse_mode='Markdown', reply_markup=create_back_button())
    else:
        bot.edit_message_text("لا توجد مستودعات لعرضها.", chat_id=call.message.chat.id, message_id=loading_message.message_id, parse_mode='Markdown', reply_markup=create_back_button())

# دالة لحذف مستودع
def handle_repo_deletion(message):
    repo_name = message.text.strip()
    user = g.get_user()
    try:
        repo = user.get_repo(repo_name)
        repo.delete()
        username = message.from_user.username
        user_link = f"[{username}](https://t.me/{username})"
        event = f"👤 *المستخدم*: {user_link}\n🗑️ *تم حذف المستودع*: `{repo_name}`"
        events.append(event)
        bot.send_message(message.chat.id, event, parse_mode='Markdown')
        if user_notifications.get(message.chat.id, True):
            notify_all_users(event)
    except:
        bot.send_message(message.chat.id, f"المستودع `{repo_name}` غير موجود أو لا تملك صلاحية حذفه.", parse_mode='Markdown')

# دالة لحذف جميع المستودعات
def delete_all_repos(call):
    user = g.get_user()
    repos = user.get_repos()
    repo_count = repos.totalCount
    for repo in repos:
        repo.delete()
    username = call.from_user.username
    user_link = f"[{username}](https://t.me/{username})"
    event = f"👤 *المستخدم*: {user_link}\n🗑️ *تم حذف جميع المستودعات*.\n📦 *عدد المستودعات المحذوفة*: {repo_count}"
    events.append(event)
    bot.edit_message_text(event, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=create_back_button())
    if user_notifications.get(call.message.chat.id, True):
        notify_all_users(event)

# دالة لعرض الأحداث
def show_events(call):
    if events:
        events_text = "\n\n".join(events)
        bot.edit_message_text(f"الأحداث:\n{events_text}", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=create_back_button())
    else:
        bot.edit_message_text("لا توجد أحداث لعرضها.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=create_back_button())

# دالة لإرسال الإشعارات لجميع المستخدمين
def notify_all_users(event):
    for user_id in users:
        if user_notifications.get(user_id, True):
            bot.send_message(user_id, f"إشعار: {event}",parse_mode='Markdown')

# التشغيل
if __name__ == "__main__":
    bot.polling()
