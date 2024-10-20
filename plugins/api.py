import pyrogram,asyncio,random
from pyrogram.raw import functions
from pyrogram import Client, filters
async def vote(session,channel, msg_id, pi):
    ap = Client(name=session[10:], api_id=21627756, api_hash='fe77fbf0cae9f7f5ece37659e2466cf1', session_string=session, workers=2, no_updates=True)
    await ap.start()
    try:
        await ap.vote_poll(channel, msg_id, [pi])
        await ap.stop()
        return True
    except:
        await ap.stop()
        return False
async def view(session, channel, msg_id):
    ap = Client(name=session[10:], api_id=21627756, api_hash='fe77fbf0cae9f7f5ece37659e2466cf1', session_string=session, workers=2, no_updates=True)
    await ap.start()
    try:
        z = await ap.invoke(functions.messages.GetMessagesViews(
                    peer= (await ap.resolve_peer(channel)),
                    id=[int(msg_id)],
                    increment=True
        ))
        await ap.stop()
        return True
    except Exception as x:
        print(x)
        await ap.stop()
        return False
async def sendmsg(session, username, text, type):
    ap = Client(name=session[10:], api_id=21627756, api_hash='fe77fbf0cae9f7f5ece37659e2466cf1', session_string=session, workers=2, no_updates=True)
    await ap.start()
    try:
        if type == 'private':
            await ap.send_message(username, text)
            await ap.stop()
            return True
        else:
            await ap.join_chat(username)
            await ap.send_message(username, text)
            await ap.leave_chat(username)
            await ap.stop()
            return True
    except:
        return False 
async def reaction(session, channel, msg_id, rs: list):
    ap = Client(name=session[10:], api_id=21627756, api_hash='fe77fbf0cae9f7f5ece37659e2466cf1', session_string=session, workers=2, no_updates=True)
    await ap.start()
    try:
        await ap.send_reaction(channel, msg_id, random.choice(rs))
        await ap.stop()
        return True
    except:
        await ap.stop()
        return False
async def members(session, channel):
    ap = Client(name=session[10:], api_id=21627756, api_hash='fe77fbf0cae9f7f5ece37659e2466cf1', session_string=session, workers=2, no_updates=True)
    await ap.start()
    try:
        await ap.join_chat(channel)
        await ap.stop()
        return True
    except:
        await ap.stop()
        return False
async def click(session, channel, msg_id):
    ap = Client(name=session[10:], api_id=21627756, api_hash='fe77fbf0cae9f7f5ece37659e2466cf1', session_string=session, workers=2, no_updates=True)
    try:
        await ap.start()
    
        try:
            await ap.join_chat(channel)
        except Exception as e:
            print(f"{e} = lol")
            pass
        g = await ap.get_messages(channel, msg_id)
        if g.reply_markup:
            x = g.reply_markup.inline_keyboard[0][0].text
            
            await g.click(x)
            
            await ap.stop()
            return True
    except:
        return False
