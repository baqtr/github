from pyrogram import Client as app, filters
from pyrogram.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
import time
from kvsqlite.sync import Client

db = Client("data.sqlite", 'fuck')
@app.on_callback_query(filters.regex("^frees$"))
async def vipsss(app, query):
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
    user_info = db.get(f"user_{user_id}")
    type = "انت مشترك مدفوع، يمكنك استخدام ميزات اكثر في القسم الاخر" if user_info['premium'] == True else 'مجاني'
    keys_1  = mk(
            [
                [btn('رشق ردود افعال ✰', 'reactions'), btn('⦅ رشق تصويت ازرار  ⦆', 'force')],
                [btn('رشق استفاء ♯', 'poll'), btn('⦅ رشق مشاهدات ⦆', 'views')],
                [btn('رجوع', 'back_home')]
            ]
        )
    rk = '''
⦗  مرحبا بك عزيزي في قسم الخدمات المجانية  ⦘
    '''
    await query.edit_message_text(rk, reply_markup=keys_1)
@app.on_callback_query(filters.regex("^vips$"))
async def vipss(app, query):
    user_id = query.from_user.id
    user_info = db.get(f"user_{user_id}")
    keys = mk(
        [
            [btn(text='رجوع', callback_data='back_home')]
        ]
    )
    if user_info['premium'] == False:
        await query.edit_message_text("عذراً ، انت غير مشترك بالـVIP !!", reply_markup=keys)
        return
    else:
        keys_1  = mk(
            [
                [btn('رشق ردود افعال ✰', 'reactions'), btn('⦅ رشق تصويت ازرار  ⦆', 'force')],
                [btn("⦅ رشق اعضاء قنوات وكروبات ⦆", 'members'), btn('رسائل سبام', 'spam')],
                [btn('رشق استفاء ♯', 'poll'), btn('⦅ رشق مشاهدات ⦆', 'views')],
                [btn('رجوع', 'back_home')]
            ]
        )
        rk ="""
⦗مرحبا بك عزيزي في قسم الخدمات المميزة ᴠɪᴘ⦘"""
        await query.edit_message_text(rk, reply_markup=keys_1)
        return