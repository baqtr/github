from pyrogram import Client as app, filters
from pyrogram.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
import time
from .reply_callbacks import invte_call
from .start_msg import startm
from kvsqlite.sync import Client

db = Client("data.sqlite", 'fuck')

@app.on_callback_query(filters.regex("^back_invite$"))
async def backback_invite(app, query):
    await invte_call(app, query)
@app.on_callback_query(filters.regex("^back_home$"))
async def h(app, query):
    await app.delete_messages(query.message.chat.id, query.message.id)
    await startm(app, query)