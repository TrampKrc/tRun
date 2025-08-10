"""
Quick start
https://docs.pyrogram.org/intro/quickstart
"""
import asyncio
#import utils as U

RUN = False

if RUN:
    import os, sys
    sys.path.append( 'D:/Cloud/OneDrive/Bot/V2/venv-vm-dev1/Lib/site-packages')

from pyrogram import Client
#import tools as T, utils as U

# 1: create file app_account for new session
app_account = "S:\\V3\\Devl\\Files\\App050325"
api_id = 20246582
api_hash = "74537ee5514115f17bcf349068a5340b"

async def main1():

    print( "comment me\n")
    return

    async with Client( app_account, api_id, api_hash) as app:
        # to create a new session file;
        # after that, app_id and api_hash can be avoided
        await app.send_message("me", "Greetings from **Pyrogram**!")

# 2: # check app_account session
async def test1():
    app = Client( app_account )
    async with app:
        # Send a message, Markdown is enabled by default
        await app.send_message("me", "Hi!") # msg to Saved Messages chanel

asyncio.run( main1() )
asyncio.run( test1() )

