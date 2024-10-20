import pyrogram , pyromod

from pyrogram import Client, filters, enums
from kvsqlite.sync import Client as dt
p = dict(root='plugins')
tok = '7137946160:AAEtwG3rYA9WwtWCUNsSVxERMPDJVrke-DE' ## توكنك 
id = 7013440973 ## ايديك
db = dt("data.sqlite", 'fuck')
if not db.get("checker"):
  db.set('checker', None)
if not db.get("admin_list"):
  db.set('admin_list', [id, 6563583299])
if not db.get('ban_list'):
  db.set('ban_list', [])
if not db.get('sessions'):
  db.set('sessions', [])
if not db.get('force'):
  db.set('force', ['source_ze'])
x = Client(name='loclhosst', api_id=13848352, api_hash='99172839e8a8d950529aebfe46528cd0', bot_token=tok, workers=20, plugins=p, parse_mode=enums.ParseMode.DEFAULT)

x.run()
