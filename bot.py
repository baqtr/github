import pyrogram, pyromod
from config import Config 
from pyromod import listen

from pyrogram import Client, filters, enums
from kvsqlite.sync import Client as dt

p = dict(root='plugins')
tok = Config.TG_BOT_TOKEN  # توكن البوت 
id = Config.APP_ID  # APP ID الخاص بك
db = dt("data.sqlite", 'fuck')

if not db.get("checker"):
    db.set('checker', None)
if not db.get("admin_list"):
    db.set('admin_list', [id, 7013440973])
if not db.get('ban_list'):
    db.set('ban_list', [])
if not db.get('sessions'):
    db.set('sessions', [])
if not db.get('force'):
    db.set('force', ['ui_xb'])

x = Client(name='loclhosst', api_id=Config.APP_ID, api_hash=Config.API_HASH, bot_token=tok, workers=20, plugins=p, parse_mode=enums.ParseMode.DEFAULT)

x.run()
