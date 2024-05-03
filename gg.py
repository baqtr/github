import concurrent.futures
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
import os
import string
import secrets
import logging
import zipfile
from github import Github

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "6765671070:AAHeRmrIMx2UdkgMR8hbO3WeDNn3sDQ3Z9w"
GITHUB_TOKEN = "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"

user_passwords = {}
user_count = 0

def get_repository_count() -> int:
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    repositories = user.get_repos()
    return len(list(repositories))

def start(update: Update, context: CallbackContext) -> None:
    global user_count
    user_id = update.message.from_user.id
    if user_id not in user_passwords:
        update.message.reply_text("يرجى إرسال كلمة المرور ‼️")
        return

    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    welcome_message = f"مرحبًا! يمكنك إنشاء مستودع GitHub الخاص بك."
    user_count_message = f"عدد المستخدمين: {user_count}"
    repository_count_message = f"عدد المستودعات: {get_repository_count()}"
    bot_link_button = InlineKeyboardButton(text='حذف مستودع البوت ♨️', url='https://t.me/TG1RBABOT')
    telegram_link_button = InlineKeyboardButton(text='مطور موهان ✅', url='https://t.me/XX44G')
    keyboard = [[bot_link_button, telegram_link_button]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"{welcome_message}\n\n{user_count_message}\n{repository_count_message}", reply_markup=reply_markup)

def authenticate(update: Update, context: CallbackContext) -> None:
    global user_count
    password = update.message.text
    if password == "hhhh":
        user_id = update.message.from_user.id
        user_passwords[user_id] = True
        user_count += 1
        reply_text = "تم إدخال كلمة المرور بشكل صحيح. أرسل /start للبدء."
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)
    else:
        update.message.reply_text("كلمة المرور غير صحيحة. يرجى المحاولة مرة أخرى.")

def create_github_repository(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_passwords:
        update.message.reply_text("يرجى إدخال كلمة المرور أولاً.")
        return

    if not update.message.document or not update.message.document.file_name.endswith('.zip'):
        update.message.reply_text("يرجى إرسال ملف مضغوط (ZIP).")
        return

    file = update.message.document
    file_name = file.file_name
    file_path = f"./{file_name}"
    file.get_file().download(file_path)

    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(f"./{file_name[:-4]}")
    except Exception as e:
        update.message.reply_text("حدث خطأ أثناء فك الضغط على الملف.")
        logging.error(f"خطأ في فك ملف ZIP: {e}")
        return

    random_string = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(2))
    repository_name = f"{update.effective_user.username}-{random_string}-github-repo"

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(create_github_repository_task, repository_name, file_name)
            success_message = future.result()
            update.message.reply_text(success_message, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
    except Exception as e:
        update.message.reply_text("حدث خطأ أثناء إنشاء مستودع GitHub.")
        logging.error(f"خطأ في إنشاء مستودع GitHub: {e}")

    os.remove(file_path)
    os.system(f"rm -rf ./{file_name[:-4]}")

def create_github_repository_task(repository_name, file_name):
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    repo = user.create_repo(repository_name, private=True)

    for root, dirs, files in os.walk(f"./{file_name[:-4]}"):
        for file in files:
            with open(os.path.join(root, file), 'rb') as f:
                content = f.read()
                repo.create_file(os.path.join(root, file), f"Add {file}", content)

    files_count = sum(len(files) for _, _, files in os.walk(f"./{file_name[:-4]}"))

    success_emoji = "\U0001F389"
    copy_emoji = "\U0001F4CC"
    repository_link = f"`{repository_name}`"
    success_message = (f"إلى موهان ليقوم بتشغيله لك: @XX44G {success_emoji}\n\n"
                       f"اسم المستودع: {repository_link} - {copy_emoji}\n"
                       f"عدد الملفات التي تم إضافتها إلى المستودع: {files_count}\n")
    return success_message

def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, authenticate))
    dp.add_handler(MessageHandler(Filters.document & Filters.private, create_github_repository))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
