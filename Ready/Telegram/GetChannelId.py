
import os

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','Lib')))


import asyncio
import config as acfg, tools as T
from TClient import TClient

async def start():

    cfg_file = os.path.join( acfg.cfg_files, "cfg-new-channel.json")
    jdata = T.CfgJson(cfg_file=cfg_file )

    app = TClient( jdata )

    # fi = ["Мастерство трейдинга", "YK_S1",]
    # await app.FindChannelId( fi, stop=False, limit=4)

    new_channel_ids = await app.FindChannelId( None, stop=False, limit=24)
    print( new_channel_ids )
    if len( new_channel_ids ) > 0:
        T.save_to_json( os.path.join( acfg.cfg_files, "channel_names3.json"), new_channel_ids)


if __name__ == '__main__':
    asyncio.run( start() )
