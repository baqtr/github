from pyromod import listen
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram import enums
from pyrogram import Client as temp
import json, time , os
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from pyrogram.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
from kvsqlite.sync import Client as uu
db = uu('dbs/elhakem.ss', 'rshq')
def adds(session: str, phone: str)-> bool:
    d = db.get('accounts')
    d.append({"s":session, 'phone': phone})
    db.set("accounts", d)
    return True

try:
    w = json.loads(open('config.json', 'r+').read())
except:
    print('[config.json] Is not exists.. Exit...')

app = Client('::memory::', in_memory=True, api_hash='f8835482f0740d5aaa27c8e07013f4a9', api_id=9886513, lang_code="ar", bot_token=w['give_bot_token'])

@app.on_message(filters.command(['start']))
async def ec(app, message):
    await generate_session(app, message)
    
async def generate_session(app, message):
    password = None 
    phone = None
    code = None
    msg = message
    api_id = 9886513
    api_hash = "f8835482f0740d5aaa27c8e07013f4a9"
    ask = await app.ask(message.chat.id,"• ارسل الان رقم الهاتف الخاص بك مع رمز الدولة \n• مثال: \n+20466133155")
    if ask.text == "/start":
    	await ec(app,message)
    	return
    if "+" not in ask.text:
        await message.reply("• رجاء ارسل رقم الهاتف بشكل صحيح")
        return
    try:
        phone = str(ask.text)
    except:
        return
    c = None
    
    
    client_1 = Client(name="user", api_id=api_id, api_hash=api_hash,lang_code="ar", in_memory=True)
    await client_1.connect()
    try:
        code = await client_1.send_code(phone)
    except (ApiIdInvalid,):
        await message.reply("• هناك مشكلة في البوت حاليا ، رجاء  قم بابلاغ المطور بهذه المشكلة")
        return
    except (PhoneNumberInvalid,):
        await message.reply("• حدث خطا في ارسال رمز التحقق الي رقم الهاتف {ask.text}\n• رجاء اعد محاولة تسجيل الرقم بشكل صحيح")
        return
    try:            
        code_e = await app.ask(message.chat.id, f"• تم ارسال كود التحقق الي رقم الهاتف {ask.text}\n\n• ارسل الان كود التحقق بين كل رقم (-)\n• مثال : \n1-2-3-4-5", timeout=20000)
            
    except TimeoutError:
        await msg.reply('• استغرقت العملية وقت اطول من اللازم ، رجاء اعادة تسجيل الرقم من جديد')
        return
    code_r = code_e.text.replace("-",'')
    try:
        await client_1.sign_in(phone, code.phone_code_hash, code_r)
        txt = await client_1.export_session_string()
        adds(txt, phone)
        await msg.reply(f"• تم اضافة وتسجيل رقم الحساب بنجاح ✅")
    except (PhoneCodeInvalid,):
        await msg.reply("• حدث خطا ما ❌\n• لقد ادخلت الكود بشكل خاطئ",reply_markup=mk([[btn(text='رجوع',callback_data='back_home')]]))
        return
    except (PhoneCodeExpired):
        await msg.reply("• حدث خطا ما ❌\n• انتهت صلاحية هذا الكود",reply_markup=mk([[btn(text='رجوع',callback_data='back_home')]]))
        return
    except (SessionPasswordNeeded):
        try:
            pas_ask = await app.ask(message.chat.id,"• تم التحقق من صحة الرمز\n\n• ارسل الان رمز التحقق بخطوتين لمتابعة التسجيل",timeout=20000)
        except:
            return
        password = pas_ask.text
        try:
            await client_1.check_password(password=password)
        except:
            msg.reply("• فشل في تسجيل الدخول ❌\n\n• رمز التحقق بخطوتين غير صحيح")
            return
        txt = await client_1.export_session_string()
        adds(txt, phone)
        await msg.reply(f"• تم اضافة وتسجيل رقم الحساب بنجاح ✅")
        return
@app.on_message(filters.private & filters.regex("^/ceasarc$"), group=2)
async def startm(app, msg):
    user_id = msg.from_user.id
    if db.get("ban_list") is None:
        db.set('ban_list', [])
        pass
    if user_id in db.get("ban_list"):
        return
    if db.exists(f"user_{user_id}"):
        keys = mk(
            [
                [btn(text=f'تنظيف', callback_data='clear')],
            ]
        )
        rk = f'''•☎️] مرحبا بك في قسم تنظيف الحسابات︎'''
        await msg.reply(rk, reply_markup=keys,quote=True)
@app.on_callback_query(filters.regex('^clear$'))
async def clear(app, call):
    if not db.exists('accounts'):
        await call.edit_message_text('• لا يوجد اي ارقام في البوت الخاص بك')
        return
    
    sessions = db.get('accounts')
    if len(sessions) < 1:
        await call.edit_message_text('لا يوجد اي ارقام في البوت الخاص بك')
        return
    
    deleted_count = 0
    working_count = 0
    print(len(sessions))
    
    await call.answer('• برجاء الانتظار \n• جارى بدء عملية التنظيف', show_alert=True)
    
    updated_sessions = []
    
    for session in sessions:
        sessio = session['s']
        phon = session['phone']
        try:
            client = temp('::memory::', api_id=9886513, api_hash='f8835482f0740d5aaa27c8e07013f4a9', in_memory=True, session_string=sessio)
        except Exception as a:
            print(a)
            continue
        
        try:
            await client.start()
        except Exception as a:
            print(a)
            deleted_count += 1
            continue
        
        try:
            await client.get_me()
            working_count += 1
            updated_sessions.append({"s":sessio, 'phone': phon})
        except Exception as a:
            print(a)
            deleted_count += 1
    
    await call.edit_message_text(f'• تم انتهاء فحص وتنظيف الحسابات ♻️\n\n• الحسابات التي تعمل ✅ : {working_count} \n\n• الحسابات التي لا تعمل ❌ : {deleted_count}')
    return
app.run()