from pyrogram import Client as app, filters
from pyrogram import Client as Co
from pyrogram.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
import time
from kvsqlite.sync import Client as xxx
from .api import *
db = xxx("data.sqlite", 'fuck')
checker = db.get('checker')
@app.on_callback_query(filters.regex("^spam$"))
async def spam_r(app, query):
    
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
    user_info = db.get(f'user_{user_id}')
    spam_price = int(db.get("price_spam")) if db.exists("price_spam") else 12
    ask1 = await app.ask(user_id, f'كم رسالة تريد ترسل؟ ', filters=filters.user(user_id))
    try:
        count = int(ask1.text)
    except:
        await ask1.reply("الارقام فقط مقبولة.. عيد من جديد.")
        return
    ask2 = await app.ask(user_id, 'الحين ارسل معرف لكروب ، او لحساب.',filters=filters.user(user_id))
    type = None
    channel = None
    try:
        inf = await app.get_chat(ask2.text)
        if str(inf.type) == 'ChatType.PRIVATE':
            type = 'private'
            channel = ask2.text
        else:
            type = 'channel'
            channel = ask2.text
    except:
        await ask2.reply("  الحساب او الكروب، مو موجود او غير معرف. رجاءا تحقق من المعرف وعيد لمحاولة.")
        return
    x = int(count) * spam_price / 2
    if user_info['coins'] < int(x):
        await ask2.reply(f"نقاطك غير كافية لشراء اعضاء بقيمة {int(x)} ، حاول تجميع نقاط اولاً .")
        return
    if int(x) <1:
        await ask2.reply("العدد صغير جداَ ..")
        return
    else:
        tex = await app.ask(user_id, "الحين أرسل رسالتك، الي تبي تسوي فيها سبام.,",filters=filters.user(user_id))
        if tex.text:
            y = 0
            ses = db.get("sessions")
            if int(count) > int(len(ses)):
                await ask2.reply("العدد كلش جبير بلنسبة لحسابات البوت ..")
                return
            for i in range(int(count)):
                try:
                    o = await sendmsg(ses[i], str(channel), tex.text, str(type))
                except Exception as m:
                    print(m)
                    continue
                if o:
                    y+=1
                else:
                    continue
            for i in range(y):
                user_info['coins'] = int(user_info['coins']) - int(spam_price) 
            db.set(f"user_{user_id}", user_info)
            await tex.reply(f"اكتملت العملية بنجاح...\nالنتائج:\nارسال ناجح: {y} .\nالطلب: {count} .\n .")
            return
@app.on_callback_query(filters.regex('^force$'))
async def force_s(app, query):
    user_id = query.from_user.id
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
    user_info = db.get(f'user_{user_id}')
    force_price = int(db.get("price_force")) if db.exists("price_force") else 12
    ask1 = await app.ask(user_id, f'كم تصويت تريد ترسل؟ ',filters=filters.user(user_id))
    try:
        count = int(ask1.text)
    except:
        await ask1.reply("الارقام فقط مقبولة.. عيد من جديد.")
        return
    x = count * int(force_price)  /2
    if count <1:
        await ask1.reply("حط رقم اعلى من هذا الرقم؟!")
        return
    if user_info['coins'] < int(x):
        await ask1.reply(f"نقاطك غير كافية لشراء اعضاء بقيمة {int(x)} ، حاول تجميع نقاط اولاً .")
        return
    else:
        ask2 = await app.ask(user_id, 'ارسل رابط المنشور الان ..?',filters=filters.user(user_id))
        channel = None
        post = None
        if ask2.text and "t.me" in ask2.text:
            channel_and_post = ask2.text.replace('https://t.me/', '').split('/')
            channel, post = channel_and_post[0], channel_and_post[1]
            
            
            try:
                
                xp = await app.get_messages(str(channel), int(post))
            except:
                await ask2.reply("المنشور ممسوح للاسف :(")
                return
            x = int(count) * int(force_price)  / 2
            y = 0
            ses = db.get("sessions")
            if int(count) > int(len(ses)):
                await ask2.reply("العدد كلش جبير بلنسبة لحسابات البوت ..")
                return
            for i in range(count):
                try:
                    o = await click(ses[i], str(channel), int(post))
                except Exception as x:
                    
                    continue
                if o:
                    y+=1
                else:
                    continue
            for j in range(y):
                user_info['coins'] = int(user_info['coins']) - int(force_price) 
            db.set(f"user_{user_id}", user_info)
            await ask2.reply(f"اكتملت العملية بنجاح...\nالنتائج:\nارسال ناجح: {y} .\nالطلب: {count} .\n .")
            return
@app.on_callback_query(filters.regex('^members$'))
async def members_S(app, query):
    user_id = query.from_user.id
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
    user_info = db.get(f'user_{user_id}')
    members_price = int(db.get("price_members")) if db.exists("price_members") else 12
    ask1 = await app.ask(user_id, f'كم عضو تريد ترسل؟ ',filters=filters.user(user_id))
    try:
        count = int(ask1.text)
    except:
        await ask1.reply("الارقام فقط مقبولة.. عيد من جديد.")
        return
    if count <1:
        await ask1.reply("حط رقم اعلى من هذا الرقم؟!")
        return
    x = count * int(members_price)  /2
    if user_info['coins'] < int(x):
        await ask2.reply(f"نقاطك غير كافية لشراء اعضاء بقيمة {int(x)} ، حاول تجميع نقاط اولاً .")
        return
    else:
        ask2 = await app.ask(user_id, 'ارسل رابط القناة او الكروب معرف او رابط..?',filters=filters.user(user_id))
        channel = None
        post = None
        if ask2.text:
            c = ask2.text.replace('https://t.me/', '').replace("@", ''); channel = c
            
            x = int(count) * int(members_price)  / 2
            y = 0
            ses = db.get("sessions")
            if int(count) > int(len(ses)):
                await ask2.reply("العدد كلش جبير بلنسبة لحسابات البوت ..")
                return
            for i in range(count):
                try:
                    o = await members(ses[i], str(channel))
                except Exception as x:
                    continue
                if o:
                    y+=1
                else:
                    continue
            for j in range(y):
                user_info['coins'] = int(user_info['coins']) - int(members_price) 
            db.set(f"user_{user_id}", user_info)
            await ask2.reply(f"اكتملت العملية بنجاح...\nالنتائج:\nارسال ناجح: {y} .\nالطلب: {count} .\n .")
            return
@app.on_callback_query(filters.regex("^poll$"))
async def poll_s(app, query):
    user_id = query.from_user.id
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
    user_info = db.get(f'user_{user_id}')
    poll_price = int(db.get("price_poll")) if db.exists("price_poll") else 12
    ask1 = await app.ask(user_id, 'كم استفتاء تبي ترسل؟ ',filters=filters.user(user_id))
    try:
        count = int(ask1.text)
    except:
        await ask1.reply("الارقام فقط الي تنقبل!")
        return
    if count <1:
        await ask1.reply("حط رقم اعلى من هذا الرقم؟!")
        return
    x = count * int(poll_price)  /2
    if user_info['coins'] < int(x):
        await ask1.reply(f"نقاطك غير كافية لشراء اعضاء بقيمة {int(x)} ، حاول تجميع نقاط اولاً .")
        return
    ask2 = await app.ask(user_id, 'الحين ارسل رابط المنشور؟؟',filters=filters.user(user_id))
    if 't.me' in ask2.text:
        channel_and_post = ask2.text.replace('https://t.me/', '').split('/')
        channel, post = channel_and_post[0], channel_and_post[1]
        try:
            x = await app.get_messages(str(channel), int(post))
            if x.poll:
                question = x.poll.question
                mm = 'الاختيارات الموجوده:\n'
                for i in x.poll.options:
                    data = i.data.decode('utf-8')
                    text = i.text
                    mm+=f"<strong>{text}</strong> > <code>{data}</code>\n"
                mm+="الحين ارسل رقم التصويت ..\nملاحظه: الرقم الي تكدر تنسخه هو الي لازم تدزه، مقابيله الاختيار الخاص بيه .."
        except Exception as r:
            await ask2.reply("الرسالة ممسوحة او القناة/كروب معرفها غلط ..")
            return
            
        ask3 = await app.ask(user_id, mm)
        ses = db.get("sessions")
        y = 0
        for i in range(count):
            try:
                o = await vote(ses[i], str(channel), int(post), int(ask3.text))
            except:
                continue
            if o:
                y+=1
            else:
                continue
        for j in range(y):
            user_info['coins'] = int(user_info['coins']) - int(poll_price) 
        db.set(f"user_{user_id}", user_info)
        await ask2.reply(f"اكتملت العملية بنجاح...\nالنتائج:\nارسال ناجح: {y} .\nالطلب: {count} .\n .")
        return
    
@app.on_callback_query(filters.regex("^reactions$"))
async def reaction_s(app, query):
    user_id = query.from_user.id
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
    user_info = db.get(f'user_{user_id}')
    reaction_price = int(db.get("reaction_poll")) if db.exists("reaction_poll") else 12
    ask = await app.ask(user_id, 'كم ريأكشن تبي ترسل ؟',filters=filters.user(user_id))
    if ask.text:
        try:
            count = int(ask.text)
        except:
            await ask.reply("الارقام فقط الي مقبولة ..")
            return
        
        ask1 = await app.ask(user_id, 'قم بأرسال رابط المنشور الان؟؟',filters=filters.user(user_id))
        
        if ask1.text and "t.me" in ask1.text:
            channel_and_post = ask1.text.replace('https://t.me/', '').split('/')
            channel, post = channel_and_post[0], channel_and_post[1]
            
            try:
                
                xp = await app.get_messages(str(channel), int(post))
            except Exception as e:
                print(e)
                await ask1.reply("المنشور ممسوح للاسف :(")
                return
        x = count * int(reaction_price)  / 2
        if int(x) > int(user_info['coins']):
            await ask1.reply(f"مامعك سعر الريأكشنات تحتاج: {x} دينار .")
            return
        if count <1:
            await ask1.reply("العدد صغير جداً .")
            return
        ses = db.get("sessions")
        y = 0
        
        bw = await app.get_chat(channel)
        b = bw.available_reactions
        if b == None:
            await ask1.reply("القناة او الكروب، مبي ريأكشنات او ممفعلهم .")
            return
        
        
        xx = []
        for e in b.reactions:
            xx.append(e.emoji)
        
        mm = "الريأكشنات الموجوده: \n"
        for i in xx:
            mm+=f'{i}\n'
        await ask1.reply(mm)
        for i in range(count):
            try:
                o = await reaction(ses[i], str(channel), int(post), xx)
            except Exception as x:
                print(x)
                continue
            if o:
                y+=1
        for i in range(y):
            user_info['coins'] = int(user_info['coins']) - int(reaction_price) 
        db.set(f"user_{user_id}", user_info)
        await ask1.reply(f"اكتملت العملية بنجاح...\nالنتائج:\nارسال ناجح: {y} .\nالطلب: {count} .\n .")
        return
@app.on_callback_query(filters.regex("^views$"))
async def vieww_s(app, query):
    user_id = query.from_user.id
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
    user_info = db.get(f'user_{user_id}')
    view_price = int(db.get("view_poll")) if db.exists("view_poll") else 12
    ask = await app.ask(user_id, 'كم مشاهدة تبي ترسل ؟',filters=filters.user(user_id))
    if ask.text:
        try:
            count = int(ask.text)
        except:
            await ask.reply("الارقام فقط الي مقبولة ..")
            return
        
        ask1 = await app.ask(user_id, 'قم بأرسال رابط المنشور الان؟؟',filters=filters.user(user_id))
        if ask1.text and "t.me" in ask1.text:
            channel_and_post = ask1.text.replace('https://t.me/', '').split('/')
            channel, post = channel_and_post[0], channel_and_post[1]
            
            try:
                
                xp = await app.get_messages(str(channel), int(post))
            except:
                await ask1.reply("المنشور ممسوح او لقناة مموجوده ..")
                return
        x = count * int(view_price) / 2
        if int(x) > int(user_info['coins']):
            await ask1.reply(f"مامعك سعر الريأكشنات تحتاج: {x} دينار .")
            return
        if count <1:
            await ask1.reply("العدد صغير جداً .")
            return
        ses = db.get("sessions")
        y = 0
        for i in range(count):
            try:
                o =await view(ses[i], str(channel), int(post))
            except:
                continue
            if o:
                y+=1
        for i in range(y):
            user_info['coins'] = int(user_info['coins']) - int(view_price) 
        db.set(f"user_{user_id}", user_info)
        await ask1.reply(f"اكتملت العملية بنجاح...\nالنتائج:\nارسال ناجح: {y} .\nالطلب: {count} .\n .")
        return
