import telebot
from telebot import types
import fitz  # PyMuPDF
import io
from pdf2image import convert_from_path
import pikepdf

# ضع هنا توكن البوت الخاص بك
API_TOKEN = '7035086363:AAG_DSbJppFhb1rcsfXdmDs4xOUbzvjdJUU'

bot = telebot.TeleBot(API_TOKEN)

# معالجة البدء /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('إضافة علامة مائية', callback_data='add_watermark')
    item2 = types.InlineKeyboardButton('استخراج الصور', callback_data='extract_images')
    item3 = types.InlineKeyboardButton('دمج ملفات PDF', callback_data='merge_pdfs')
    item4 = types.InlineKeyboardButton('تقسيم ملفات PDF', callback_data='split_pdf')
    item5 = types.InlineKeyboardButton('تحويل PDF إلى صور', callback_data='pdf_to_images')
    item6 = types.InlineKeyboardButton('تحويل صور إلى PDF', callback_data='images_to_pdf')
    markup.add(item1, item2, item3, item4, item5, item6)

    bot.send_message(message.chat.id, "أهلاً بك! اختر إحدى الخيارات:", reply_markup=markup)

# معالجة الضغط على الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'add_watermark':
        bot.send_message(call.message.chat.id, "أرسل لي ملف PDF لإضافة علامة مائية.")
        bot.register_next_step_handler(call.message, watermark_step)
    elif call.data == 'extract_images':
        bot.send_message(call.message.chat.id, "أرسل لي ملف PDF لاستخراج الصور.")
        bot.register_next_step_handler(call.message, extract_images_step)
    elif call.data == 'merge_pdfs':
        bot.send_message(call.message.chat.id, "أرسل لي ملفات PDF لدمجها.")
        bot.register_next_step_handler(call.message, merge_pdfs_step)
    elif call.data == 'split_pdf':
        bot.send_message(call.message.chat.id, "أرسل لي ملف PDF لتقسيمه.")
        bot.register_next_step_handler(call.message, split_pdf_step)
    elif call.data == 'pdf_to_images':
        bot.send_message(call.message.chat.id, "أرسل لي ملف PDF لتحويله إلى صور.")
        bot.register_next_step_handler(call.message, pdf_to_images_step)
    elif call.data == 'images_to_pdf':
        bot.send_message(call.message.chat.id, "أرسل لي الصور لتحويلها إلى PDF.")
        bot.register_next_step_handler(call.message, images_to_pdf_step)

def watermark_step(message):
    if message.document.mime_type == 'application/pdf':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('document.pdf', 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, "أرسل لي النص الذي تود إضافته كعلامة مائية.")
        bot.register_next_step_handler(message, apply_watermark)
    else:
        bot.send_message(message.chat.id, "الرجاء إرسال ملف PDF صالح.")

def apply_watermark(message):
    watermark_text = message.text
    doc = fitz.open('document.pdf')
    for page in doc:
        page.insert_text((100, 100), watermark_text, fontsize=20, color=(0, 0, 1))
    doc.save('watermarked.pdf')
    with open('watermarked.pdf', 'rb') as pdf_file:
        bot.send_document(message.chat.id, pdf_file)
    bot.send_message(message.chat.id, "تمت إضافة العلامة المائية بنجاح!")

def extract_images_step(message):
    if message.document.mime_type == 'application/pdf':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('document.pdf', 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, "جار استخراج الصور...")
        extract_images(message)
    else:
        bot.send_message(message.chat.id, "الرجاء إرسال ملف PDF صالح.")

def extract_images(message):
    images = convert_from_path('document.pdf')
    for i, image in enumerate(images):
        image.save(f'page_{i}.png', 'PNG')
        with open(f'page_{i}.png', 'rb') as img_file:
            bot.send_photo(message.chat.id, img_file)
    bot.send_message(message.chat.id, "تم استخراج الصور بنجاح!")

def merge_pdfs_step(message):
    bot.send_message(message.chat.id, "أرسل لي ملفات PDF واحدًا تلو الآخر. ارسل 'انتهيت' عندما تكون جاهزًا.")
    pdf_files = []
    bot.register_next_step_handler(message, lambda m: collect_pdfs(m, pdf_files))

def collect_pdfs(message, pdf_files):
    if message.text.lower() == 'انتهيت':
        if len(pdf_files) < 2:
            bot.send_message(message.chat.id, "يجب أن ترسل ملفين PDF على الأقل للدمج.")
        else:
            bot.send_message(message.chat.id, "جار دمج الملفات...")
            merged_pdf = pikepdf.Pdf.new()
            for pdf_file in pdf_files:
                src_pdf = pikepdf.Pdf.open(io.BytesIO(pdf_file))
                merged_pdf.pages.extend(src_pdf.pages)
            merged_pdf.save('merged.pdf')
            with open('merged.pdf', 'rb') as pdf_file:
                bot.send_document(message.chat.id, pdf_file)
            bot.send_message(message.chat.id, "تم دمج الملفات بنجاح!")
    else:
        if message.document.mime_type == 'application/pdf':
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            pdf_files.append(downloaded_file)
            bot.send_message(message.chat.id, "أرسل ملف PDF آخر أو اكتب 'انتهيت' للدمج.")
        else:
            bot.send_message(message.chat.id, "الرجاء إرسال ملف PDF صالح.")
        bot.register_next_step_handler(message, lambda m: collect_pdfs(m, pdf_files))

def split_pdf_step(message):
    if message.document.mime_type == 'application/pdf':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('document.pdf', 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, "جار تقسيم الملف...")
        doc = fitz.open('document.pdf')
        for i in range(len(doc)):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
            new_doc.save(f'page_{i + 1}.pdf')
            with open(f'page_{i + 1}.pdf', 'rb') as pdf_file:
                bot.send_document(message.chat.id, pdf_file)
        bot.send_message(message.chat.id, "تم تقسيم الملف بنجاح!")
    else:
        bot.send_message(message.chat.id, "الرجاء إرسال ملف PDF صالح.")

def pdf_to_images_step(message):
    if message.document.mime_type == 'application/pdf':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('document.pdf', 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, "جار تحويل الملف إلى صور...")
        images = convert_from_path('document.pdf')
        for i, image in enumerate(images):
            image.save(f'page_{i}.png', 'PNG')
            with open(f'page_{i}.png', 'rb') as img_file:
                bot.send_photo(message.chat.id, img_file)
        bot.send_message(message.chat.id, "تم تحويل الملف إلى صور بنجاح!")
    else:
        bot.send_message(message.chat.id, "الرجاء إرسال ملف PDF صالح.")

def images_to_pdf_step(message):
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(f'image_{message.photo[-1].file_id}.png', 'wb') as img_file:
            img_file.write(downloaded_file)
        bot.send_message(message.chat.id, "أرسل صورة أخرى أو اكتب 'انتهيت' للدمج.")
        bot.register_next_step_handler(message, lambda m: collect_images(m, [f'image_{message.photo[-1].file_id}.png']))
    else:
        bot.send_message(message.chat.id, "الرجاء إرسال صورة صالحة.")

def collect_images(message, image_files):
    if message.text.lower() == 'انتهيت':
        if len(image_files) < 1:
            bot.send_message(message.chat.id, "يجب أن ترسل صورة واحدة على الأقل.")
        else:
            bot.send_message(message.chat.id, "جار دمج الصور...")
            images = [fitz.open(image_file).convert_to_pdf() for image_file in image_files]
            merged_pdf = fitz.open()
            for img_pdf in images:
                merged_pdf.insert_pdf(img_pdf)
            merged_pdf.save('images_to_pdf.pdf')
            with open('images_to_pdf.pdf', 'rb') as pdf_file:
                bot.send_document(message.chat.id, pdf_file)
            bot.send_message(message.chat.id, "تم تحويل الصور إلى ملف PDF بنجاح!")
    else:
        if message.photo:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_file = f'image_{message.photo[-1].file_id}.png'
            with open(image_file, 'wb') as img_file:
                img_file.write(downloaded_file)
            image_files.append(image_file)
            bot.send_message(message.chat.id, "أرسل صورة أخرى أو اكتب 'انتهيت' للدمج.")
        else:
            bot.send_message(message.chat.id, "الرجاء إرسال صورة صالحة.")
        bot.register_next_step_handler(message, lambda m: collect_images(m, image_files))

# تشغيل البوت
bot.polling()
