from pyrogram import Client as app, filters
from pyrogram.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
import time
from .start_msg import startm
from kvsqlite.sync import Client

db = Client("data.sqlite", 'fuck')
@app.on_message(filters.private & filters.regex("^/r$"))
async def t(app, msg):
    z = db.keys()
    for i in z:
        try:
            u = i[0]
            info = db.get(f"{u}")
            id = info["id"]
            print(id)
        except Exception as b:
            continue
        try:
            
            info["coins"] = int(info["coins"]) + 100
            db.set(f"user_{id}", info)
        except: pass
    await msg.reply("ok")

@app.on_message(filters.private & filters.regex("^/start (.*?)"))
async def e(app, msg):
    join_user = msg.from_user.id
    to_user = int(msg.text.split("/start ")[1])
    if join_user == to_user:
        return
    if not db.exists(f"user_{join_user}"):
        someinfo = db.get(f"user_{to_user}")
        if join_user in someinfo['users']:
            await startm(app, msg)
            return
        else:
            dd = db.get('invite_price')
            someinfo['users'].append(join_user)
            someinfo['coins'] = int(someinfo['coins'])  + dd
            info = {'coins': 0 , 'id': join_user, 'premium': False, 'admin': False, "phone":[], "users":[], "date":str(time.time())}
            db.set(f'user_{join_user}', info)
            db.set(f'user_{to_user}', someinfo)
            await app.send_message(to_user, f'فات {msg.from_user.mention} لرابط دعوتك، واخذت 300 أرصدة ..')
            await startm(app, msg)
            return
    else:
        await startm(app, msg)
        return