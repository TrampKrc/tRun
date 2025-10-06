import os
import asyncio
from pyrogram import Client

import config as acfg
import tools as T


"""
should define 
   Run()
   Close()
"""

class TClient( T.CfgAPI ):

    Tclient: Client
    #cfgJson: CfgJson

    is_running: bool

    def __init__(self, cfgJson ) -> None:

        super().__init__( cfgJson )
        session = acfg.tg_session

        if os.path.exists( session + '.session' ) == False:
            raise ValueError( f"Nof found Telegram session file: {session}+.session ")

        """
        if self.cfg_all.get('SessionName', None ) is None :
            s_file = acfg.tg_session
            if s_file is None:
                raise ValueError("Nof found Telegram Session file")

            if os.path.exists( s_file ):
                self._cfg_secret = T.read_json( s_file )
                session = self._cfg_secret.get('SessionName', None)
                if session is None:
                   raise ValueError("Nof found parameter Secret.SessionName")
            else:
                raise ValueError(f"Nof found cfg file: { s_file } ")
        else:
            session = self.cfg_all['SessionName']
        """

        self.Tclient = Client( session )

        """
        if section is not None:
            if self.cfg_all.get( section, None) is None:
                raise ValueError(f"Nof found parameter {section=} ")

            self._section_cfg = self.cfg_all[ section ]
            
        else:
            self._section_cfg = cfgJson.cfg_section
            

    @property
    def cfg_channel(self):
        return self._section_cfg

    
    @property
    def section_cfg(self):
        return self._section_cfg
    """

    async def FindChannelId( self, filter=None, stop=True, limit=5):
        async with self.Tclient:

#           if self.channel_cfg["Id"] == 0:
            if filter is None: filter=self.cfg_section['Name']

            id_chn = await self.find_channel_id( filter, stop, limit )
            self.logInfo(f"Channel: {id_chn}")
            return id_chn  #.values()

    async def find_channel_id( self, filter=' ', stop=True, limit=20):
        # Find channel
        k = 0
        chanel_id = {}
        # async for dialog in app.get_dialogs( 10 ):
        async for dialog in self.Tclient.get_dialogs():
            name = dialog.chat.first_name or dialog.chat.title
            if name and name in filter:
                # print(dialog.chat.first_name or dialog.chat.title, dialog.chat.id, dialog.chat.is_restricted ) #, dialog.chat.members_count)
                print(f"'{name}' : ", dialog.chat.id, ',')

                # chanel_id = { 'name': name, 'id': dialog.chat.id }
                chanel_id[name] = dialog.chat.id
                k += 1
                if k % 100 == 0:
                    print(k)

                if stop or k > limit:
                    break

        print("Total chanells: ", k)

        if k > len(chanel_id):
            self.print_r("More than one chanel with same name.")
            self.print_r(chanel_id)
            raise Exception("More than one chanel with name %s\n" % filter)

        return chanel_id

    async def find_channel_ids( self, filter=' '):
        # Find channel
        channel_ids = {}
        # async for dialog in app.get_dialogs( 10 ):
        all_channels = f_channels = 0

        #gg = self.Tclient.get_dialogs()

        async for dialog in self.Tclient.get_dialogs():
            name = dialog.chat.first_name or dialog.chat.title
            all_channels += 1
            if name and name in filter:
                channel_ids[name] = dialog.chat.id
                print(f'"{name}" : ', dialog.chat.id, ',')
                f_channels += 1
                if f_channels == len(filter): break

        print( f"Channels: { len( filter) }, Found: { f_channels }; Total channels: {all_channels}" )

        return channel_ids


    async def TClient_Start(self):

        async with self.Tclient:
            """
            if self.channel_cfg.get("Id",0) == 0:
                id_chn = await self.find_channel_id( filter=self.channel_cfg['Name'], stop=False, limit=4)

                if len(id_chn) == 0:
                    raise Exception("No channel with name %s\n" % self.channel_cfg['Name'])

                if len(id_chn) > 1:
                    self.logError("More than one channel with this name.", id_chn )
                    raise Exception("More than one channel with name %s\n" % self.channel_cfg['Name'])

                self.channel_cfg["Id"] = id_chn[self.channel_cfg['Name']]
                self.logInfo(f"Find channelId { self.channel_cfg['Id']} for channel {id_chn[self.channel_cfg['Name']]}")
            """
            await self.Run()

            self.Close()

    async def Run(self):
        pass

    def Close(self):
        pass

# ===========================

async def telegram_main():

    section = "Channel"
    jdata = T.CfgJson(cfg_file="../Files/cfg-test.json", section=section)

    Bot = TClient( jdata, section )
    await Bot.TClient_Start()


if __name__ == '__main__':
    from colorPrint import colorPrint as cp
    cp.p_green('PyCharm')
    asyncio.run(telegram_main())
