from pyrogram import Client as app, filters
from pyrogram.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
import time
from kvsqlite.sync import Client

db = Client("data.sqlite", 'fuck')

@app.on_callback_query(filters.regex("^invite$"))
async def invte_call(app, query):
    user_id = query.from_user.id
    chats = db.get('force')
    from .force import check_channel_member
    for i in chats:
      if not await check_channel_member(app, i, user_id):
        k = f'''
عذراً عزيزي 🤚 
عليك الاشتراك بقناة البوت لتتمكن من أستخدامهُ :
- @{i}
- @{i}
— — — — — — — — — —
قم بلأشتراك، وأرسل /start .
        '''
        return await query.edit_message_text(k, reply_markup=mk([[btn(f'- @{i} .', url=f't.me/{i}')]]))
    keys = mk(
        [
            [btn(text='مشاركة رابط الدعوة', callback_data='sharelink'), btn(text='هدية يومية', callback_data='dailygift')],
            
            [btn(text='رجوع', callback_data='back_home')],
        ]
    )
    rk = """
مرحبا بك في قسم ⦅ تجميع الرصيد ⦆ 
هنالك ثلاث طرق لتجميع الرصيد ✰
 1 - مشاركة رابط الدعوة ⥋ 
 2 - تسليم ارقام تليجرام للمطور 
3 - الهدية اليومية 🎁
    """
    await query.edit_message_text(rk, reply_markup= keys)
@app.on_callback_query(filters.regex("^account$"), group=2)
async def acc(app, query):
    user_id = query.from_user.id
    chats = db.get('force')
    from .force import check_channel_member
    for i in chats:
      if not await check_channel_member(app, i, user_id):
        k = f'''
عذراً عزيزي 🤚 
عليك الاشتراك بقناة البوت لتتمكن من أستخدامهُ :
- @{i}
- @{i}
— — — — — — — — — —
قم بلأشتراك، وأرسل /start .
        '''
        return await query.edit_message_text(k, reply_markup=mk([[btn(f'- @{i} .', url=f't.me/{i}')]]))
    keys = mk(
        [
            
            [btn('رجوع', 'back_home')]
        ]
    )
    info = db.get(f"user_{query.from_user.id}")
    if info:
        coins = info['coins']
        users = len(info['users'])
        prem = 'مدفوع' if info['premium'] == True else 'مجاني'
        rk = f"""
⥳ معلومات حسابك 
⥃ رصيد حسابك الان ⤶ IQD {coins}
⥃ عدد مشاركتك لرابط الدعوه ⤶ {users}
⥃ نوع اشتراكك الان ⤶ {prem}
———
        """
        await query.edit_message_text(rk, reply_markup=keys)
    else:
        return
@app.on_callback_query(filters.regex("^buy$"))
async def b(app, query):
    user_id = query.from_user.id
    chats = db.get('force')
    from .force import check_channel_member
    for i in chats:
      if not await check_channel_member(app, i, user_id):
        k = f'''
عذراً عزيزي 🤚 
عليك الاشتراك بقناة البوت لتتمكن من أستخدامهُ :
- @{i}
- @{i}
— — — — — — — — — —
قم بلأشتراك، وأرسل /start .
        '''
        return await query.edit_message_text(k, reply_markup=mk([[btn(f'- @{i} .', url=f't.me/{i}')]]))
    rk  = """
⥃ لشراء الرصيد من بوت الخدمات 
- @UP_UO
    """
    keys = mk(
        [
            
            [btn('رجوع', 'back_home')]
        ]
    )
    await query.edit_message_text(rk, reply_markup=keys)
@app.on_callback_query(filters.regex("^trans$"))
async def transs(app, query):
    user_id = query.from_user.id
    chats = db.get('force')
    from .force import check_channel_member
    for i in chats:
      if not await check_channel_member(app, i, user_id):
        k = f'''
عذراً عزيزي 🤚 
عليك الاشتراك بقناة البوت لتتمكن من أستخدامهُ :
- @{i}
- @{i}
— — — — — — — — — —
قم بلأشتراك، وأرسل /start .
        '''
        return await query.edit_message_text(k, reply_markup=mk([[btn(f'- @{i} .', url=f't.me/{i}')]]))
    user_info = db.get(f"user_{query.from_user.id}")
    await app.delete_messages(query.message.chat.id, query.message.id)
    ask1 = await app.ask(query.from_user.id,"⤾ قم بارسال ⦗𝚒𝚍 ⦘ العضو المراد تحويل النقاط اليه ♯", filters.user(query.from_user.id))
    try:
        ids = int(ask1.text)
    except:
        await ask1.reply("تأكد يكون رقم!!، عيد العملية..")
        return
    if not db.exists(f'user_{ids}'):
        keys = mk(
        [
            [btn('رجوع', 'back_home')]
        ]
    )
        await ask1.reply("عذراً، هذا الايدي مو موجود ضمن بياناتنا", reply_markup=keys)
        return
    else:
        keys = mk(
        [
            [btn('رجوع', 'back_home')]
        ]
    )
        ask2 = await app.ask(query.from_user.id,"ارسل المبلغ الي تبي تحوله ?", filters.user(query.from_user.id))
        try:
            amount = int(ask2.text)
        except:
            await ask2.reply("تاكد يكون رقم، عيد العملية!")
            return
        if amount <1:
            await ask2.reply("المبلغ جدا صغير!!", reply_markup=keys)
            return
        if amount >= int(user_info['coins']):
            await ask2.reply("المبلغ كلش جبير، او يساوي مبلغ حسابك. او معندك ياه. قلله.",reply_markup=keys)
        else:
            to_user = db.get(f"user_{ids}")
            to_user['coins'] = int(to_user['coins']) + int(amount)
            user_info['coins'] = int(user_info['coins']) - int(amount)
            db.set(f"user_{ids}", to_user)
            db.set(f"user_{query.from_user.id}", user_info)
            await app.send_message(chat_id=ids, text=f"وصلك حوالة..\nالمبلغ: {amount} دينار .\nمن : {query.from_user.mention} | {query.from_user.id} .\nرصيدك هسه: {to_user['coins']} .")
            await ask2.reply(f"تمت عملية التحويل!!\nالمبلغ: {amount} دينار .\nمن : {query.from_user.mention} | {query.from_user.id} .\nالى : {ids} .\nرصيدك هسه: {user_info['coins']} ", reply_markup=keys)
            return
@app.on_callback_query(filters.regex("^service$"))
async def service(app, query):
    user_id = query.from_user.id
    chats = db.get('force')
    from .force import check_channel_member
    for i in chats:
      if not await check_channel_member(app, i, user_id):
        k = f'''
عذراً عزيزي 🤚 
عليك الاشتراك بقناة البوت لتتمكن من أستخدامهُ :
- @{i}
- @{i}
— — — — — — — — — —
قم بلأشتراك، وأرسل /start .
        '''
        return await query.edit_message_text(k, reply_markup=mk([[btn(f'- @{i} .', url=f't.me/{i}')]]))
    keys = mk(
        [
            [btn(text='⦗ خدمات الرشق الـ ᴠɪᴘ ⦘', callback_data='vips'), btn(text='⦗خدمات الرشق الجانية⦘', callback_data='frees')],
            [btn(text='رجوع', callback_data='back_home')],
        ]
    )
    rk = """
⥃ مرحبا بك عزيزي في بوت Services | الخدمات ♯ 
هنالك نوعين من الخدمات العادي و الـ ViP ✰
    """
    await query.edit_message_text(rk, reply_markup=keys)
    return