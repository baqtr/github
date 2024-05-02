import os
import string
import secrets
import logging
import zipfile
from github import Github
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "6915008157:AAGt0kobKSfw3ZNsS6wCWFaau1j8zgq5e9U"
GITHUB_TOKEN = "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"

def start(update: Update, context: CallbackContext) -> None:
    welcome_message = "هلا بك عزيزي يمكنك انشاء مستودع جيتهاب خاص بك وحسب اختيارك php/Python  يرجاء ارسال ملف مضغوط zip ذا كنت لاتعرف شئ قم بمراسلة موهان لكي يقوم بتعلييمك"
    bot_link_button = InlineKeyboardButton(text='بوت حذف المستودع ♨️', url='https://t.me/TG1RBABOT')
    telegram_link_button = InlineKeyboardButton(text='المطور موهان ✅', url='https://t.me/XX44G')
    keyboard = [[bot_link_button, telegram_link_button]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(welcome_message, reply_markup=reply_markup)

def create_github_repository(update: Update, context: CallbackContext) -> None:
    # Check if the message has a document
    if not update.message.document or not update.message.document.file_name.endswith('.zip'):
        update.message.reply_text("يرجى إرسال ملف مضغوط (ZIP).")
        return

    # Download the ZIP file
    file = update.message.document
    file_name = file.file_name
    file_path = f"{file_name}"
    file.get_file().download(file_path)

    # Extract the ZIP file
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
        update.message.reply_text("يحق لكل مستخدم انشاء مستودع واحد ان كنت ترييد تبديله قم بحذف المستودع الحالي ويمكنك انشاء مستودع جديد قم بحذفه من خلال ارسال اسمه لبوت الحذف :@TG1RBABOT")
        logging.error(f"Error creating GitHub repository: {e}")
        return

    # Add extracted files to the repository
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

    # Get the number of files added to the repository
    files_count = sum(len(files) for _, _, files in os.walk(f"./{file_name[:-4]}"))

    # Send success message
    success_emoji = "\U0001F389"
    copy_emoji = "\U0001F4CC"
    repository_link = f"`{repository_name}`"
    success_message = (f"{success_emoji} تم انشاءه مستودعك بنجاح قم برسال الاسم الا موهان لكي يقوم بتشغيله لك : @XX44G {success_emoji}\n\n"
                       f"اسم المستودع: {repository_link} - {copy_emoji} انقر لنسخ الاسم\n"
                       f"عدد الملفات التي تم وضعها في المستودع: {files_count}\n")
    update.message.reply_text(success_message, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')

    # Clean up: remove the ZIP file and extracted folder
    os.remove(file_path)
    os.system(f"rm -rf ./{file_name[:-4]}")

def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document & Filters.private, create_github_repository))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
