import os
import string
import secrets
import logging
import zipfile
from github import Github
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from time import sleep

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
        update.message.reply_text("يرجى إدخال كلمة المرور:")
        return

    # Delete bot's previous messages
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    # Display welcome message
    welcome_message = f"مرحبًا بك! يمكنك إنشاء مستودع GitHub خاص بك."
    user_count_message = f"عدد المستخدمين: {user_count}"
    repository_count_message = f"عدد المستودعات: {get_repository_count()}"
    bot_link_button = InlineKeyboardButton(text='بوت حذف المستودع ♨️', url='https://t.me/TG1RBABOT')
    telegram_link_button = InlineKeyboardButton(text='المطور موهان ✅', url='https://t.me/XX44G')
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
        reply_text = "تم التحقق من كلمة المرور بنجاح. مرحبًا بك!"
        # Delete bot's previous messages
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        # Display welcome message after 3 seconds
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)
        sleep(3)
        start(update, context)
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
        logging.error(f"Error extracting ZIP file: {e}")
        return

    random_string = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(2))
    
    repository_name = f"{update.effective_user.username}-{random_string}-github-repo"
    g = Github(GITHUB_TOKEN)
    user = g.get_user()

    try:
        repo = user.create_repo(repository_name, private=True)
    except Exception as e:
        update.message.reply_text("حدث خطأ أثناء إنشاء مستودع GitHub.")
        logging.error(f"Error creating GitHub repository: {e}")
        return

    try:
        for root, dirs, files in os.walk(f"./{file_name[:-4]}"):
            for file in files:
                with open(os.path.join(root, file), 'rb') as f:
                    content = f.read()
                    repo.create_file(os.path.join(root, file), f"Add {file}", content)
    except Exception as e:
        update.message.reply_text("حدث خطأ أثناء إضافة الملفات إلى المستودع.")
        logging.error(f"Error adding files to GitHub repository: {e}")
        return

    files_count = sum(len(files) for _, _, files in os.walk(f"./{file_name[:-4]}"))

    success_emoji = "\U0001F389"
    copy_emoji = "\U0001F4CC"
    repository_link = f"`{repository_name}`"
    success_message = (f"الى موهان لكي يقوم بتشغيله لك : @XX44G {success_emoji}\n\n"
                       f"اسم المستودع: {repository_link} - {copy_emoji} انقر لنسخ الاسم\n"
                       f"عدد الملفات التي تم وضوعها في المستودع: {files_count}\n")
    update.message.reply_text(success_message, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')

    os.remove(file_path)
    os.system(f"rm -rf ./{file_name[:-4]}")

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
