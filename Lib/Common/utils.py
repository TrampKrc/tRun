
import os
import sys
import asyncio

from datetime import datetime

from pyrogram import Client
#print (pyrogram.__version__)
import tools

#root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(root + '/python')

folder0 = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(folder0 + '/Code')

async def task_timer(count, period=300 ):
    print(tools.pink(f'Start timer  {count} {datetime.now()}'))
    try:
        while count > 0:
            await asyncio.sleep(1)

            if count % period == 0:
                print(tools.pink(f"Timer is working.... {count} sec"))
            count = count - 1

    except  asyncio.CancelledError as e:
        print('Exception CancelledError: timer', str(e), f'  {count}')
    
    finally:
        print(tools.pink(f'Finally timer: {count}'))
    
    print(tools.pink(f'Exit timer  {count} {datetime.now()}'))
    return count

async def send_msg( tlgApp ):
    async with tlgApp:
        # Send a message, Markdown is enabled by default
        await tlgApp.send_message("me", "Hi there! I'm using **Pyrogram**")

"""
D:\\Cloud\OneDrive\Bot\V2\venv\Scripts\python.exe D:\Cloud\OneDrive\Bot\V2\tlgclient-2.py
{
    "_": "Chat",
    "id": -1001676828687,
    "type": "ChatType.CHANNEL",
    "is_verified": false,
    "is_restricted": false,
    "is_creator": false,
    "is_scam": false,
    "is_fake": false,
    "title": "API by Cryptonec",
    "photo": {
        "_": "ChatPhoto",
        "small_file_id": "AQADAgADc8QxG37W6UkAEAIAA_GPaMcW____gaMoy9QSkn8ABB4E",
        "small_photo_unique_id": "AgADc8QxG37W6Uk",
        "big_file_id": "AQADAgADc8QxG37W6UkAEAMAA_GPaMcW____gaMoy9QSkn8ABB4E",
        "big_photo_unique_id": "AgADc8QxG37W6Uk"
    },
    "description": "По всем вопросам обращаться строго по контактам ниже‼️\n\n@kryptonec_official\n@ATM_machine_cryptonec",
    "dc_id": 2,
    "has_protected_content": false,
    "pinned_message": {
        "_": "Message",
        "id": 5255,
        "sender_chat": {
            "_": "Chat",
            "id": -1001676828687,
            "type": "ChatType.CHANNEL",
            "is_verified": false,
            "is_restricted": false,
            "is_creator": false,
            "is_scam": false,
            "is_fake": false,
            "title": "API by Cryptonec",
            "photo": {
                "_": "ChatPhoto",
                "small_file_id": "AQADAgADc8QxG37W6UkAEAIAA_GPaMcW____gaMoy9QSkn8ABB4E",
                "small_photo_unique_id": "AgADc8QxG37W6Uk",
                "big_file_id": "AQADAgADc8QxG37W6UkAEAMAA_GPaMcW____gaMoy9QSkn8ABB4E",
                "big_photo_unique_id": "AgADc8QxG37W6Uk"
            },
            "dc_id": 2,
            "has_protected_content": false
        },
        "date": "2023-03-09 14:30:01",
        "chat": {
            "_": "Chat",
            "id": -1001676828687,
            "type": "ChatType.CHANNEL",
            "is_verified": false,
            "is_restricted": false,
            "is_creator": false,
            "is_scam": false,
            "is_fake": false,
            "title": "API by Cryptonec",
            "photo": {
                "_": "ChatPhoto",
                "small_file_id": "AQADAgADc8QxG37W6UkAEAIAA_GPaMcW____gaMoy9QSkn8ABB4E",
                "small_photo_unique_id": "AgADc8QxG37W6Uk",
                "big_file_id": "AQADAgADc8QxG37W6UkAEAMAA_GPaMcW____gaMoy9QSkn8ABB4E",
                "big_photo_unique_id": "AgADc8QxG37W6Uk"
            },
            "dc_id": 2,
            "has_protected_content": false
        },
        "mentioned": false,
        "scheduled": false,
        "from_scheduled": false,
        "edit_date": "2023-03-09 19:27:37",
        "has_protected_content": false,
        "text": "Уважаемы инвесторы, закройте, пожалуйста, все позиции\n\nРиск необходимо изменить с 2% на 0.3%\n\nBot Configuration > Trading > client name > General > Amount per Trade > Percentage и пишете текстом 0.3\n\nСпасибо!",
        "entities": [
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.BOLD",
                "offset": 0,
                "length": 208
            }
        ],
        "views": 326,
        "forwards": 6,
        "outgoing": false,
        "reactions": {
            "_": "MessageReactions",
            "reactions": []
        }
    },
    "can_set_sticker_set": false,
    "members_count": 206,
    "available_reactions": {
        "_": "ChatReactions",
        "reactions": [
            {
                "_": "Reaction",
                "emoji": "🥰"
            },
            {
                "_": "Reaction",
                "emoji": "🔥"
            },
            {
                "_": "Reaction",
                "emoji": "💔"
            },
            {
                "_": "Reaction",
                "emoji": "👏"
            },
            {
                "_": "Reaction",
                "emoji": "👍"
            },
            {
                "_": "Reaction",
                "emoji": "❤"
            }
        ]
    }
}

Process finished with exit code 0

"""

"""
{
    "_": "Message",
    "id": 70405,
    "sender_chat": {
        "_": "Chat",
        "id": -1001266391544,
        "type": "ChatType.CHANNEL",
        "is_verified": false,
        "is_restricted": false,
        "is_creator": false,
        "is_scam": false,
        "is_fake": false,
        "title": "Indicator by Cryptonec",
        "photo": {
            "_": "ChatPhoto",
            "small_file_id": "AQADAgADsr8xG84lCEoAEAIAAwhW398W____JqObZwuAJW8ABB4E",
            "small_photo_unique_id": "AgADsr8xG84lCEo",
            "big_file_id": "AQADAgADsr8xG84lCEoAEAMAAwhW398W____JqObZwuAJW8ABB4E",
            "big_photo_unique_id": "AgADsr8xG84lCEo"
        },
        "dc_id": 2,
        "has_protected_content": false
    },
    "date": "2023-03-24 12:35:59",
    "chat": {
        "_": "Chat",
        "id": -1001266391544,
        "type": "ChatType.CHANNEL",
        "is_verified": false,
        "is_restricted": false,
        "is_creator": false,
        "is_scam": false,
        "is_fake": false,
        "title": "Indicator by Cryptonec",
        "photo": {
            "_": "ChatPhoto",
            "small_file_id": "AQADAgADsr8xG84lCEoAEAIAAwhW398W____JqObZwuAJW8ABB4E",
            "small_photo_unique_id": "AgADsr8xG84lCEo",
            "big_file_id": "AQADAgADsr8xG84lCEoAEAMAAwhW398W____JqObZwuAJW8ABB4E",
            "big_photo_unique_id": "AgADsr8xG84lCEo"
        },
        "dc_id": 2,
        "has_protected_content": false
    },
    "forward_from_chat": {
        "_": "Chat",
        "id": -1001528138841,
        "type": "ChatType.CHANNEL",
        "is_verified": false,
        "is_restricted": false,
        "is_creator": false,
        "is_scam": false,
        "is_fake": false,
        "title": "VIP 3.0 HANDMADE",
        "photo": {
            "_": "ChatPhoto",
            "small_file_id": "AQADAgADVb8xG5fuUUkAEAIAA6djRdAW____YpkjZEXKhuQABB4E",
            "small_photo_unique_id": "AgADVb8xG5fuUUk",
            "big_file_id": "AQADAgADVb8xG5fuUUkAEAMAA6djRdAW____YpkjZEXKhuQABB4E",
            "big_photo_unique_id": "AgADVb8xG5fuUUk"
        },
        "dc_id": 2,
        "has_protected_content": false
    },
    "forward_from_message_id": 7106,
    "forward_date": "2023-03-24 10:50:46",
    "reply_to_message_id": 70404,
    "reply_to_message": {
        "_": "Message",
        "id": 70404,
        "sender_chat": {
            "_": "Chat",
            "id": -1001266391544,
            "type": "ChatType.CHANNEL",
            "is_verified": false,
            "is_restricted": false,
            "is_creator": false,
            "is_scam": false,
            "is_fake": false,
            "title": "Indicator by Cryptonec",
            "photo": {
                "_": "ChatPhoto",
                "small_file_id": "AQADAgADsr8xG84lCEoAEAIAAwhW398W____JqObZwuAJW8ABB4E",
                "small_photo_unique_id": "AgADsr8xG84lCEo",
                "big_file_id": "AQADAgADsr8xG84lCEoAEAMAAwhW398W____JqObZwuAJW8ABB4E",
                "big_photo_unique_id": "AgADsr8xG84lCEo"
            },
            "dc_id": 2,
            "has_protected_content": false
        },
        "date": "2023-03-24 12:35:59",
        "chat": {
            "_": "Chat",
            "id": -1001266391544,
            "type": "ChatType.CHANNEL",
            "is_verified": false,
            "is_restricted": false,
            "is_creator": false,
            "is_scam": false,
            "is_fake": false,
            "title": "Indicator by Cryptonec",
            "photo": {
                "_": "ChatPhoto",
                "small_file_id": "AQADAgADsr8xG84lCEoAEAIAAwhW398W____JqObZwuAJW8ABB4E",
                "small_photo_unique_id": "AgADsr8xG84lCEo",
                "big_file_id": "AQADAgADsr8xG84lCEoAEAMAAwhW398W____JqObZwuAJW8ABB4E",
                "big_photo_unique_id": "AgADsr8xG84lCEo"
            },
            "dc_id": 2,
            "has_protected_content": false
        },
        "forward_from_chat": {
            "_": "Chat",
            "id": -1001528138841,
            "type": "ChatType.CHANNEL",
            "is_verified": false,
            "is_restricted": false,
            "is_creator": false,
            "is_scam": false,
            "is_fake": false,
            "title": "VIP 3.0 HANDMADE",
            "photo": {
                "_": "ChatPhoto",
                "small_file_id": "AQADAgADVb8xG5fuUUkAEAIAA6djRdAW____YpkjZEXKhuQABB4E",
                "small_photo_unique_id": "AgADVb8xG5fuUUk",
                "big_file_id": "AQADAgADVb8xG5fuUUkAEAMAA6djRdAW____YpkjZEXKhuQABB4E",
                "big_photo_unique_id": "AgADVb8xG5fuUUk"
            },
            "dc_id": 2,
            "has_protected_content": false
        },
        "forward_from_message_id": 7096,
        "forward_date": "2023-03-24 02:14:33",
        "mentioned": false,
        "scheduled": false,
        "from_scheduled": false,
        "has_protected_content": false,
        "text": "#HANDMADE_SESSION(полуавтоматическая торговля)\n\nИндикатор обнаружил точку входа в #SHORT🤿❗️\n\nПара #IOTXUSDT\n\nСсылка для быстрого открытия сделки 💥\n\nТекущая цена(беру по рынку) entry 0.02558 (30% вашего размера позиции)\n\n1st limit order: entry 0.02660 (35% вашего размера позиции)\n\n2nd limit order: entry 0.02788 (35% вашего размера позиции)\n\nTake Profit 1: 0.02520\n\nTake Profit 2: 0.02456\n\nTake Profit 3: 0.02353\n\nStop loss: 0.02967\n\nExchanges: Bybit USDT, Binance Futures",
        "entities": [
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.HASHTAG",
                "offset": 0,
                "length": 17
            },
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.HASHTAG",
                "offset": 82,
                "length": 6
            },
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.HASHTAG",
                "offset": 99,
                "length": 9
            },
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.TEXT_LINK",
                "offset": 110,
                "length": 35,
                "url": "https://www.binance.com/ru/futures/IOTXUSDT?_from=markets"
            },
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.CODE",
                "offset": 184,
                "length": 7
            },
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.CODE",
                "offset": 245,
                "length": 7
            },
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.CODE",
                "offset": 306,
                "length": 7
            },
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.CODE",
                "offset": 359,
                "length": 9
            },
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.CODE",
                "offset": 383,
                "length": 9
            },
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.CODE",
                "offset": 407,
                "length": 9
            },
            {
                "_": "MessageEntity",
                "type": "MessageEntityType.CODE",
                "offset": 427,
                "length": 9
            }
        ],
        "views": 1,
        "forwards": 0,
        "outgoing": false
    },
    "mentioned": false,
    "scheduled": false,
    "from_scheduled": false,
    "media": "MessageMediaType.PHOTO",
    "has_protected_content": false,
    "has_media_spoiler": false,
    "caption_entities": [
        {
            "_": "MessageEntity",
            "type": "MessageEntityType.HASHTAG",
            "offset": 34,
            "length": 9
        },
        {
            "_": "MessageEntity",
            "type": "MessageEntityType.ITALIC",
            "offset": 126,
            "length": 81
        },
        {
            "_": "MessageEntity",
            "type": "MessageEntityType.HASHTAG",
            "offset": 237,
            "length": 9
        }
    ],
    "photo": {
        "_": "Photo",
        "file_id": "AgACAgIAAx0CS3uZ-AABARMFZB37oLw_Z5QmjNw_fUVLZRU2kRMAAq7EMRvvEvBI8wpGEkL8fIgACAEAAwIAA3gABx4E",
        "file_unique_id": "AgADrsQxG-8S8Eg",
        "width": 657,
        "height": 155,
        "file_size": 12978,
        "date": "2023-03-24 10:50:46"
    },
    "caption": "4.00%(Х20 - 80%)✅\n\nПрофит по паре #IOTXUSDT в 4.00% достигнут за 08ч 04м\n\n2 цели взято, всех поздравляем, стоп в безубытке💎\n\n______________________________________________________________________________\n\n\n4.00%(Х20 -  80%)✅\n\nProfit by #IOTXUSDT pair of 4.00% was gained in 08ч 04m\n\n2 takes done, congratulations to all, stop at entry💎",
    "views": 1,
    "forwards": 0,
    "outgoing": false
}

"""

async def print_channel_history( tlgApp, chat_id, limit):

    k = 0
    async for message in tlgApp.get_chat_history( chat_id, limit ):
        print( '=======================')
        print( k, message.date )
        print( message.text)
        k -= 1

async def get_chanel_history( tApp, c_id, dateStart, dateEnd=0, limit=32000):

    date_start = datetime.fromisoformat( dateStart )
    date_end = datetime.now() if dateEnd == 0 else datetime.fromisoformat( dateEnd )

    resp = []

#    async with tApp:
    k = 0
    n = 0
    async for message in tApp.get_chat_history( c_id, limit, offset_date = date_end ):

        #print(++n, tools.blue(message.date))
        #print(message.text)

        if message.text != None:
            k += 1
            if message.date <= date_start:
                print( tools.pink('this msg is skipped =======================') )
                print( k, tools.pink(message.date))
                print(message.text)
                break

            #print('==>>>>>')
            print( k, tools.yellow(message.date))
            #print(message.text)

            resp.append( message )

    resp.reverse()
    return resp

async def get_chanel_history_by_name( tApp, c_name, dateStart, dateEnd=0, limit=32000):
    # datetime(2024, 3, 20, 18, 55, 00 ) )
    # date_min = datetime.fromisoformat('2024-03-20 20:00:00')
    # date_max = datetime.fromisoformat('2024-03-20 21:00:00')

    # date_now     = datetime.now()
    # date_now_utc = datetime.utcnow()

    date_start = datetime.fromisoformat( dateStart )
    date_end = datetime.now() if dateEnd == 0 else datetime.fromisoformat( dateEnd )

    resp = []

    async with tApp:
        # await find_channel()
        chn = await find_channel_id( tApp, filter= c_name )
        k = 0
        n = 0
        # async for message in app.get_chat_history( chn[ c_name ], 15 ):
        async for message in tApp.get_chat_history( chn[ c_name ], limit, offset_date = date_end ):

            print(++n, tools.blue(message.date))
            print(message.text)

            if message.text != None:
                k += 1
                if message.date <= date_start:
                    print( tools.pink('this msg is skipped =======================') )
                    print( k, tools.pink(message.date))
                    print(message.text)
                    break

                print('==>>>>>')
                print( k, tools.yellow(message.date))
                print(message.text)

                resp.append( message )

    resp.reverse()
    return resp




async def write_channel_file( tlgApp, chat_id, limit, name):
    
    try:
        with open(name + '.txt', 'w', encoding="utf-8") as fo:
          async for msg in tlgApp.get_chat_history(chat_id, limit):

            print('--->>>', msg )
            print('--->>>', msg.date, msg.text)

            fo.write(f'==> {msg.date}\n')
            if msg.text and ( 'Индикатор обнаружил' in msg.text or 'Профит по паре' in msg.text ):
                fo.write('msg.text :')
                fo.write(msg.text)
                
            if msg.caption and 'Профит по паре' in msg.caption:
                fo.write('msg.caption :')
                fo.write(msg.caption)
                ll = msg.caption.split('✍️')
                fo.write(f'\nExtract: {ll[0]}\n')

            fo.write( '\n====================\n' )

    except IOError as msg:
        sys.stderr.write("Can't open: %s\n" % name)

async def read_channel_file( name ):
    msgs = []
    try:
        msg = ''
        with open( name + '.txt', 'r', encoding="utf-8") as f:
          for line in f:
            if '==>' in line:
                if len( msg ) > 3:
                   msgs.append(msg)
                   msg = ''
                continue
            else:
              msg += line
              
          msgs.append(msg) # add last msg
    
    except IOError as msg:
        sys.stderr.write("Can't open: %s\n" % name)
      
    return msgs

if __name__ == '__main__':
    #asyncio.run( GetChannelId() )
    pass


"""
#f = filters.chat(Indicator_by_Cryptonec) | filters.chat(INPUT__testchannel)
f = filters.chat(Indicator_by_Cryptonec)
@app.on_message(f)
def my_handler(client, message):
    print(message)
    # copy() so there's no "forwarded from" header
    #message.copy(chat_id=OUTPUT__MT_FORWARD_CHAT_ID,  caption="")
"""




