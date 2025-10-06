"""
Quick start
https://docs.pyrogram.org/intro/quickstart
"""

import os
import asyncio

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','Lib')))

from pyrogram import Client
import config as acfg

# 1: create file app_account for new session
#app_account = acfg.cfg_files + "\\App050325"
#app_account_file = acfg.cfg_files + "\\App081925"

app_account = acfg.tg_session
app_account_file = acfg.tg_session

#api_id = 20246582
#api_hash = "74537ee5514115f17bcf349068a5340b"

# 09/24/2025
api_id = 29573264
api_hash = "1c647a24b8fdf3508123a9e4d95a41f7"



channels = {
    'YK-Sig':   -1001754270660,
    'YK_S1':    -1001400228409,
    'Открытки': -1001727534323,
    'ToStudy':  -1001722743781,

    'YevTBD_F': -1001796988910,
    'X1':       -1002008182150
}



async def init():

    print( "comment me\n")

    async with Client( app_account_file, api_id, api_hash) as app:
        # to create a new session file;
        # after that, app_id and api_hash can be avoided
        await app.send_message("me", "Greetings from **Pyrogram**!")

# 2: # check app_account session
async def send_msg():

    where = 'me'
    #where = channels['YK-Sig']
    #where = channels['YevTBD_F']

    app = Client( app_account )
    async with app:
        # Send a message, Markdown is enabled by default
        await app.send_message(where, "Hi!") # msg to Saved Messages chanel


async def get_chat():
    app = Client( app_account )
    async with app:

        c_id = channels['YK-Sig']

        #chat = await app.get_chat("pyrogram")
        #print(chat)

        #chat = await app.get_chat( c_id )
        #print(chat)

        #async for message in app.get_chat_history( c_id, 5 ):
        #    print(message.text)

        await app.leave_chat( channels['X1'] )
        #print ( 'leave')

        #chat = await app.get_chat( channels['X1'] )

        #chat = await app.get_chat( channels['YevTBD_F'] )
        #print(chat)

async def test3():
    from pyrogram import enums

    chat_id = yk_s1
    app = Client( app_account )

    async with app:

        # Get members
        async for member in app.get_chat_members(chat_id):
            print(member)

        # Get administrators
        administrators = []
        async for m in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            administrators.append(m)

        print( f"Administrators: { administrators }" )

async def my_private_channel_info():
    channels = {
        'YK-Sig': -1001754270660,
        'YK_S1': -1001400228409,
        'Открытки': -1001727534323,
        'ToStudy': -1001722743781
    }

    app = Client( app_account )
    async with app:
        for name, chat_id in channels.items():

            chat = await app.get_chat(chat_id)
            print(f"Channel: {name=}:" )
            print(chat)

async def all_channels():
    app = Client( app_account )
    channel_id = {}

    async with app:
        #me = await app.get_me()
        #print(me)

        count = await app.get_dialogs_count()
        print(count)

        # async for dialog in app.get_dialogs( 10 ):
        async for dialog in app.get_dialogs(500):
            name = dialog.chat.first_name or dialog.chat.title
            if name:
                channel_id[name] = dialog.chat.id

    total = len( channel_id )
    print("Total chanelles: ", total)

    if total > 0:

        sorted_names = sorted( channel_id.keys() )
        with open("all_channels.txt", 'wt', encoding="utf-8") as fout:
            #for name, id in channel_id.items():
            for name in sorted_names:
                fout.write( f"'{name}' : {channel_id[name]}\n" )


if __name__ == '__main__':
    #asyncio.run( init() )
    asyncio.run( send_msg() )

    #asyncio.run( get_chat() )
    #asyncio.run( my_private_channel_info() )
    #asyncio.run( all_channels() )
    #asyncio.run( test2() )

