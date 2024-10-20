from pyromod import listen
from pyrogram.types import Message
from pyrogram import Client as app, filters
from pyrogram import Client 
from pyrogram import enums
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
from kvsqlite.sync import Client as xxx
from .api import *
db = xxx("data.sqlite", 'fuck')
def adds(session: str)-> bool:
    d = db.get('sessions')
    d.append(session)
    db.set("sessions", d)
    return True
async def generate_session(app,message):
    password = None 
    phone = None
    code = None
    msg = message
    api_id = 21627756
    api_hash = "fe77fbf0cae9f7f5ece37659e2466cf1"
    ask = await app.ask(
        message.chat.id,
        "[ علمود تسجل، ارسل رقمك هسة ]\n- مثال: \n+12054092413 ..",
    )
    try:
        phone = str(ask.text)
    except:
        return
    c = None
    
    
    client_1 = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client_1.connect()
    try:
        code = await client_1.send_code(phone)
    except (ApiIdInvalid,):
        await message.reply("اكو مشكلة عامه من البوت ..",reply_markup=mk([[btn(text='رجوع',callback_data='back_home')]]))
        return
    except (PhoneNumberInvalid,):
        await message.reply("اكو مشكلة عامه من البوت..",reply_markup=mk([[btn(text='رجوع',callback_data='back_home')]]))
        return
    try:            
        code_e = await app.ask(message.chat.id, "[ تم ارسال كود تحقق الى حسابك ]\n- قم بأرسالة على هاذا النحو :\n 1 2 3 4 5 ", timeout=20000)
            
    except TimeoutError:
        
        await msg.reply('[ الوقت الي أخذته العملية كلش طويل ، عيد من جديد .. ]',reply_markup=mk([[btn(text='رجوع',callback_data='back_home')]]))
        return
    code_r = code_e.text.replace(" ",'')
    try:
        await client_1.sign_in(phone, code.phone_code_hash, code_r)
        txt = await client_1.export_session_string()
        adds(txt)
        await msg.reply(f"[ تم إضافة الرقم ].",reply_markup=mk([[btn(text='رجوع',callback_data='back_home')]]))
    except (PhoneCodeInvalid,):
        await msg.reply("[ الكود خطا ] ",reply_markup=mk([[btn(text='رجوع',callback_data='back_home')]]))
        return
    except (PhoneCodeExpired):
        await msg.reply("[ الكود منتهيه صلاحيته ]",reply_markup=mk([[btn(text='رجوع',callback_data='back_home')]]))
        return
    except (SessionPasswordNeeded):
        try:
            pas_ask = await app.ask(
                message.chat.id,
                "[ حسابك فيه تحقق بخطوتين، ارسل الرمز هسة ] ..",timeout=20000)
        except:
            return
        password = pas_ask.text
        try:
            await client_1.check_password(password=password)
        except:
            msg.reply("[ باسوورد غلط ]!!",reply_markup=mk([[btn(text='رجوع',callback_data='back_home')]]))
            return
        txt = await client_1.export_session_string()
        adds(txt)
        await msg.reply(f"[ تم إضافة الرقم ].",reply_markup=mk([[btn(text='رجوع',callback_data='back_home')]]))
        return
    