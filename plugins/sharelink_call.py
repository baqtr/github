from pyrogram import Client as app, filters
from pyrogram.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
import time
from kvsqlite.sync import Client

db = Client("data.sqlite", 'fuck')

@app.on_callback_query(filters.regex("^sharelink$"))
async def sharelinkk(app, query):
    user_id = query.from_user.id
    bot_username = None
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
    cq = 250 if not db.get("invite_price") else db.get("invite_price")
    try:
        c  = await app.get_me()
        bot_username = c.username
    except:
        await query.edit_message_text("حدث خطأ بالبوت ، حاول لاحقاً .")
        return
    keys = mk(
        [
            [btn(text='رجوع', callback_data='back_invite')],
        ]
    )
    link = f"https://t.me/{bot_username}?start={user_id}"
    rk = f"""
اهلا بك عزيزي،
قسم مشاركة رابط الدعوه!
رابط الدعوة الخاص بك هو: {link} .
⎯ ⎯ ⎯ ⎯
على كل عضو يفوت للبوت من رابطك تحصل على {cq} أرصده.
    """
    await query.edit_message_text(rk, reply_markup=keys)