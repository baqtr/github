from pyrogram import Client as app, filters
from pyrogram import Client as temp
from pyrogram.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
import time
from kvsqlite.sync import Client

db = Client("data.sqlite", 'fuck')

admins = db.get('admin_list')
@app.on_message(filters.private & filters.command(['admin']), group=5)
async def ade(app, msg):
    user_id = msg.from_user.id
    user_info = db.get(f'user_{user_id}')
    num = len(db.get("sessions"))
    
    if user_id in admins:
        keys = mk(
            [
                [btn('اضافة ادمن', 'add_admin'), btn('حذف ادمن', 'delete_admin')],
                [btn('احصائيات البوت', 'stats')],
                [btn('اضافة نقاط لشخص', 'add_coins'), btn('خصم نقاط من شخص', 'less_coin')],
                [btn('اذاعه', 'brod')],
                [btn('جلب معلومات شخص', 'get_info'), btn('حظر عضو', 'ban_me')],
                [btn('رفع حظر عضو', 'unban_me')],
                [btn('تعيين سعر منتج ', 'set_price'), btn('تسليم ارقام', 'gen')],
                [btn(f'عدد ارقام لبوت: {num}', 'nonee')],
                [btn('تفعيل مدفوع', 'onp'), btn('انهاء مدفوع', 'offp')],
                [btn('تعيين قنوات اشتراك .', 'setforce')],
                [btn('تعيين حساب تحقق', 'addch'), btn('تنظيف لحسابات .', 'clear')]
                
            ]
        )
        await msg.reply("اهلا بك عزيزي الادمن", reply_markup=keys)
@app.on_callback_query(filters.regex("^add_admin$"), group=6)
async def ad_admin(app, query):
    user_id = query.from_user.id
    print(admins)
    if user_id in admins:
        askk = await app.ask(user_id, 'اوكي هسه ارسل ايدي الشخص لتريد تضيفة.. شرط يكون مسوي ستارت للبوت!!')
        if askk.text:
            try:
                t_id = int(askk.text)
            except:
                await askk.reply("خوية، ارسل ايدي مثل الاوادم.")
                return
            if db.exists("admin_list"):
                s = db.get("admin_list")
                s.append(t_id)
                db.set('admin_list', s)
                await askk.reply(f"تم اضافة: {t_id}, كـ ادمن بالبوت ..")
                return
            else:
                db.set("admin_list", [])
                s = db.get("admin_list")
                s.append(t_id)
                db.set('admin_list', s)
                await askk.reply(f"تم اضافة: {t_id}, كـ ادمن بالبوت ..")
                return
        else:
            pass
@app.on_callback_query(filters.regex("^delete_admin$"), group=7)
async def ada_admin(app, query):
    user_id = query.from_user.id
    if user_id in admins:
        askk = await app.ask(user_id, 'اوكي هسه ارسل ايدي الشخص لتريد تحذفه.. شرط يكون مسوي ستارت للبوت!!')
        if askk.text:
            try:
                t_id = int(askk.text)
            except:
                await askk.reply("خوية، ارسل ايدي مثل الاوادم.")
                return
            if db.exists("admin_list"):
                s = db.get("admin_list")
                s.remove(t_id)
                db.set('admin_list', s)
                await askk.reply(f"تم مسح: {t_id}, من ادمنية البوت ..")
                return
            else:
                db.set("admin_list", [])
                s = db.get("admin_list")
                s.append(t_id)
                db.set('admin_list', s)
                await askk.reply(f"تم مسح: {t_id}, من ادمنية البوت ..")
                return
        else:
            pass
def calculate_inflation(total: float, previous_total: float) -> int:
    inflation_rate = (total - previous_total) / previous_total * 100
    
    # قيمة النسبة لا يمكن أن تزيد عن 100
    if inflation_rate > 100:
        inflation_rate = 100
    
    # تقريب النسبة إلى القيمة الصحيحة الأقرب بين 0 و 100
    return round(max(0, min(100, inflation_rate)))
@app.on_callback_query(filters.regex("^stats$"))
async def statss(app, query):
    count = 0
    mon = 0
    users = db.keys()
    x = "معلومات البوت العامة:\n"
    for i in users:
        if "user_" in str(i[0]):
            count+=1
    x+=f'عدد اعضاء البوت: {count} .\n'
    for i in users:
        if "user_" in str(i[0]) and "gift" not in str(i[0]) or 'price_' not in str(i[0]) or 'sessions' not in str(i[0]):
            try:
                i = db.get(i[0])
                print(i)
                mon+=int(i['coins'])
            except:
                continue
    b = calculate_inflation(mon, mon-1000)
    x+=f'نسبة التضخم في البوت: %{b}\n'
    x+=f'عدد كل الاموال او الرصيد في البوت: {mon}\n'
    await app.send_message(query.from_user.id, x)
    return
@app.on_callback_query(filters.regex("^add_coins$"), group=8)
async def add_coinssw(app, query):
    user_id = query.from_user.id
    if user_id in admins:
        askk = await app.ask(user_id, 'اوك ارسل ايديه.. ؟')
        if askk.text:
            try:
                t_id = int(askk.text)
            except:
                await askk.reply("خوية، ارسل ايدي مثل الاوادم.")
                return
            ask2 = await app.ask(user_id, 'هسه ارسل المبلغ او العدد الي تبي تضيفه له')
            if ask2.text:
                try:
                    amount = int(ask2.text)
                except:
                    return
                b = db.get(f"user_{t_id}")
                b['coins'] = int(b['coins']) + amount
                db.set(f"user_{t_id}", b)
                await ask2.reply(f"العدد: {amount}. تمت اضافته لـ {t_id}")
                await app.send_message(int(t_id), f"⥊ تم اضافة ⦗{amount} IQD⦘ الى حسابك من قبل المطور ⥂")
                return
            else:
                pass
        else:
            pass
@app.on_callback_query(filters.regex("^less_coin$"), group=9)
async def les_co(app, query):
    user_id = query.from_user.id
    if user_id in admins:
        askk = await app.ask(user_id, 'اوك ارسل ايديه.. ؟')
        if askk.text:
            try:
                t_id = int(askk.text)
            except:
                await askk.reply("خوية، ارسل ايدي مثل الاوادم.")
                return
            ask2 = await app.ask(user_id, 'هسه ارسل المبلغ او العدد الي تبي تخصمه منه')
            if ask2.text:
                try:
                    amount = int(ask2.text)
                except:
                    return
                b = db.get(f"user_{t_id}")
                b['coins'] = int(b['coins']) - amount
                db.set(f"user_{t_id}", b)
                await ask2.reply(f"العدد: {amount}. تمت خصمه من {t_id}")
                return
            else:
                pass
        else:
            pass
@app.on_callback_query(filters.regex("^brod$"), group=10)
async def brod_ss(app, query):
    user_id = query.from_user.id
    ask1 = await app.ask(user_id, 'الحين ارسل الرساله الي تبي تدزها للأعضاء (صورة، نص, فيديو، الخ)')
    if ask1:
        c = 0
        msg_id = ask1.id
        k = db.keys()
        for i in k:
            if "user_" in str(i[0]) and "gift" not in str(i[0]) or 'price_' not in str(i[0]) or 'sessions' not in str(i[0]):
                try:
                    id = int(str(i[0]).replace("user_", ''))
                except:
                    continue
                try:
                    await app.copy_message(id, user_id, msg_id)
                    c+=1
                except:
                    continue
        await ask1.reply(f"العملية تمت بنجاح..\nتم ارسالها الى {c} شخص .")
import datetime

def ttd(timestamp) -> str:
    
    date = datetime.datetime.fromtimestamp(timestamp)
    
    
    formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_date
@app.on_callback_query(filters.regex("^get_info$"), group=11)
async def get_infso(app, query):
    user_id = query.from_user.id
    ask = await app.ask(user_id, 'ارسل ايدي الشخص? ')
    if ask.text:
        try:
            id = int(ask.text)
        except:
            return
        d = db.get(f"user_{id}")
        if d is None:
            await ask.reply("الحساب مو موجود ")
            return
        try:
            coins = d['coins']
            premium = 'مدفوع' if d['premium'] else 'مجاني'
            admin = 'نعم' if d['admin'] else 'لا'
            ddd = str(d['date']).split(".")[0]
            date = ttd(int(ddd))
        except Exception as x:
            print(x)
            return
        await ask.reply(f'معلومات حسابه:\nرصيده: {coins} .\nهل هو مدفوع ؟ : {premium} .\nهل هو ادمن؟ : {admin}\nتاريخ انشاء حسابه: {date} .')
@app.on_callback_query(filters.regex("^ban_me$"), group=12)
async def ban_mes(app, query):
    user_id = query.from_user.id
    ask = await app.ask(user_id, 'ارسل ايدي الشخص? ')
    if ask.text:
        try:
            id = int(ask.text)
        except:
            return
        d = db.get(f"user_{id}")
        if d is None:
            await ask.reply("الحساب مو موجود ")
            return
        if db.exists("ban_list"):
            dw = db.get("ban_list")
            dw.append(id)
            db.set(f"ban_list", dw)
            await ask.reply("تم حظر العضو ..")
        else:
            db.set("ban_list", [])
            dw = db.get("ban_list")
            dw.append(id)
            db.set(f"ban_list", dw)
            await ask.reply("تم حظر العضو ..")
@app.on_callback_query(filters.regex("^unban_me$"), group=13)
async def unban_me(app, query):
    user_id = query.from_user.id
    ask = await app.ask(user_id, 'ارسل ايدي الشخص? ')
    if ask.text:
        try:
            id = int(ask.text)
        except:
            return
        d = db.get(f"user_{id}")
        if d is None:
            await ask.reply("الحساب مو موجود ")
            return
        if db.exists("ban_list"):
            dw = db.get("ban_list")
            dw.remove(id)
            db.set(f"ban_list", dw)
            await ask.reply("تم الغاء حظر العضو ..")
        else:
            db.set("ban_list", [])
            dw = db.get("ban_list")
            dw.remove(id)
            db.set(f"ban_list", dw)
            await ask.reply("تم الغاء حظر العضو ..")
@app.on_callback_query(filters.regex("^set_price$"), group=14)
async def aaw(app, query):
    user_id = query.from_user.id
    prices = ['price_poll', 'price_members', 'price_force', 'price_spam', 'reaction_poll', 'view_poll']
    x = 'عزيزي هذه هي اكواد الاسعار الموجوده.. لتغير سعر احد المنتجات ارسل الكود الذي يمكنك نسخه ..\n<code>price_poll</code> - سعر منتج الاستفتاء .\n<code>price_members</code> - سعر منتج الاعضاء .\n<code>price_force</code> - سعر منتج تصويت الاجباري ولغير اجباري .\n<code>price_spam</code> - سعر منتج السبام .\n<code>reaction_poll</code> - سعر منتج التفاعلات .\n<code>view_poll</code> - سعر منتج المشاهدات .\n<code>invite_price</code> - قيمة مشاركة رابط الدعوه \n\nالحين ارسل رمز المنتج الي تبي تغيره ..?'
    ask = await app.ask(user_id, x)
    if ask.text:
        code = ask.text
        np = 12 if not db.get(code) else db.get(code)
        ask2 = await app.ask(user_id, f'السعر الحالي: {np} .\nارسل السعر لجديد ؟')
        if ask2.text:
            try:
                db.set(code, int(ask2.text))
                await ask2.reply("تم تعيين السعر الجديد ..")
            except:
                return
@app.on_callback_query(filters.regex('^gen$'), group=15)
async def aa(app, query):
    from .gen_ses import generate_session
    await generate_session(app, query.message)
@app.on_callback_query(filters.regex('^onp$'))
async def onpp(app, query):
    user_id = query.from_user.id
    ask = await app.ask(user_id, 'ارسل ايدي الشخص? ')
    if ask.text:
        try:
            id = int(ask.text)
        except:
            return
        d = db.get(f"user_{id}")
        if d is None:
            await ask.reply("العضو مو موجود")
            return
        d['premium'] = True
        db.set(f'user_{id}', d)
        await ask.reply("تم تفعيل البريميوم له .")
        await app.send_message(int(id), "⥃ مبروك تم تفعيل ⦗ᴠɪᴘ⦘ يمكنك الاستمتاع بجميع الخدمات ⥃")
        return
@app.on_callback_query(filters.regex('^offp$'))
async def offs(app, query):
    user_id = query.from_user.id
    ask = await app.ask(user_id, 'ارسل ايدي الشخص? ')
    if ask.text:
        try:
            id = int(ask.text)
        except:
            return
        d = db.get(f"user_{id}")
        if d is None:
            await ask.reply("العضو مو موجود")
            return
        d['premium'] = False
        db.set(f'user_{id}', d)
        await ask.reply("تم تعطيل البريميوم منه .")
        return
@app.on_callback_query(filters.regex('^addch$'))
async def addchh(app, call):
  ask = await app.ask(
    call.from_user.id,
    'ارسل السيشن الان'
  )
  if ask.text:
    ses = ask.text
    db.set('checker', ses)
    await ask.reply('تم تعيين السيشن ')
    return
@app.on_callback_query(filters.regex('^clear$'))
async def clear(app,call):
  if not db.exists('sessions'):
    await call.edit_message_text('مافي سيشنات معينة ياحب  ..')
    return
  if len(db.get('sessions')) < 1:
    await call.edit_message_text('مافي سيشنات ياحب ..')
    return
  ses = db.get("sessions")
  de = 0
  w = 0
  print(len(ses))
  await call.answer('سوف يأخذ بعض الوقت ..', show_alert=True)
  for i in range(len(ses)):
    try:
      c = temp('::memory::', api_id=21627756, api_hash='fe77fbf0cae9f7f5ece37659e2466cf1', in_memory=True, session_string=ses[i])
    except:
      continue
    try:
      await c.start()
    except:
      ses.remove(ses[i])
      de+=1
    try:
      await c.get_me()
      
      w+=1
    except:
      de+=1
      ses.remove(ses[i])
  db.set(f'sessions', ses)
  await call.edit_message_text(f'تم انتهاء فحص وتنظيف الحسابات..\n\nالشغال: {w} .\nالخربان: {de} .')
  return
@app.on_callback_query(filters.regex('^setforce$'))
async def setforcee(app, query):
  ask = await app.ask(
    query.from_user.id,
    'ارسل قنوات الاشتراك هكذا:\n@first @second .'
  )
  if ask.text:
    channels = ask.text.replace("@", '').split(' ')
    print(channels)
    db.set(f'force', channels)
    await ask.reply('تم تعيين القنوات بنجاح ..')
    return