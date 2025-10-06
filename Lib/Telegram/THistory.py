import asyncio
import traceback
from datetime import datetime

import tools as T
from TClient import TClient
from p_table import parser_table as pt


class THistory( TClient ):
    
    # if u need support db, should define:
    def dbInit(self, jdata):
        pass
    
    def dbOpen(self):
        pass

    def startChannel(self):
        pass

    # should be defined:
    def process_msg(self, msg):
        return False

    def closeChannel(self):
        pass

    def dbClose(self):
        pass
        

    def __init__(self, cfg_file="cfg.json", section="ChannelList", jclass=None ) -> None:

        if jclass is not None:
            jdata = jclass
        else:
            jdata = T.CfgJson( cfg_file= cfg_file, section=section)

        super().__init__( jdata, section)

        #if section == "ChannelList":
        self.channelList = self.cfg_section # list of channels to process

        """
        channel_name = ""
        if parser is None:
            channel_name = self.channel_cfg.get("Name", None )
            if channel_name:
                self.channel_parser = pt.get( channel_name, None )
        else:
            self.channel_parser = parser

        if self.channel_parser is None:
            raise ValueError( f"Parser for channel {channel_name} Nof found cfg file: {cfg_file} ")
        """
        self.dbInit( self.base )

    async def Start(self):
        self.dbOpen()
        await self.TClient_Start() # TClient_Start will call Run()

    # call from self.TClient_Start()
    async def Run(self):    # Read History

        channelName_list = list(self.channelList.keys())
        id_chn = await self.find_channel_ids(filter=channelName_list )

        if len(id_chn) == 0:
            raise Exception("No channel Ids were found" )

        for channel_name, section_desc in self.channelList.items():
            if section_desc[0] == '-':
                self.logInfo(f"Channel <{channel_name}> skipped, section starts with '-' prefix")
                continue  # skip sections with '-' prefix

            self.cfg_channel_desc = self.cfg_all.get( section_desc, None )

            if self.cfg_channel_desc is None:
                self.logError(f"Channel section {section_desc} not found in config file ")
                continue

            self.cfg_channel_desc["Name"] = channel_name
            if self.cfg_channel_desc.get("Id", 0) == 0:
                c_id = id_chn.get(channel_name, None)
                if c_id is None:
                    self.logError(f"Channel id for <{channel_name}> not found in Telegram. Check the name or Id.")
                    continue
                self.cfg_channel_desc["Id"] = c_id

            self.channel_parser = pt.get(channel_name, pt['EmptyParser'] )

            if self.channel_parser == pt['EmptyParser']:
                #raise ValueError(f"Parser for channel {channel_name} Nof found cfg file: {cfg_file} ")
                self.logError(f"Parser for channel <{channel_name}> is not implemented, using EmptyParser")

            self.logInfo(f"Read history: channelId {self.cfg_channel_desc["Id"]} - {self.cfg_channel_desc['Name']}", cl='green2')

            limit   = self.cfg_channel_desc["HistoryLimit"]

            # convert to local timezone:
            local_tz = datetime.now().astimezone().tzinfo

            s_date = self.cfg_channel_desc["HistoryStart"]
            s_date_o = datetime.fromisoformat(s_date)
            s_date_l = s_date_o.astimezone(local_tz).strftime('%Y-%m-%d %H:%M:%S')

            e_date = self.cfg_channel_desc["HistoryEnd"]
            e_date_o = datetime.fromisoformat(e_date)
            e_date_l = e_date_o.astimezone(local_tz).strftime('%Y-%m-%d %H:%M:%S') #local date

            self.logInfo(f"Original Date interval: StartDate: {s_date} EndDate: {e_date} ")
            self.logInfo(f"Read channel history: StartDate: {s_date_l} EndDate: {e_date_l} Limit: {limit}")

            self.startChannel()
            await self.get_chanel_history_cycle( self.cfg_channel_desc["Id"], s_date_l, dateEnd=e_date_l, limit=limit )
            self.closeChannel()

        self.logInfo("History reading finished.")

    # all channels had been proceed; call self.Close()

    def Close(self):
        self.dbClose()

    async def get_chanel_history_cycle( self, c_id, dateStart, dateEnd="", limit=32000 ):

        date_start = datetime.fromisoformat( dateStart )
        date_end = datetime.now() if dateEnd == "" else datetime.fromisoformat(dateEnd)

        all = 0
        text = 0
        take = 0

        async for message in self.Tclient.get_chat_history(c_id, limit, offset_date=date_end):

            #print( T.green(message.date))
            #print(message.text)
            all += 1
            if message.text != None or message.caption != None:

                text += 1

                if message.date <= date_start:
                    #print(T.pink('this msg is skipped ======================='))
                    #print(k, T.pink(message.date))
                    self.logInfo(f"Last Message. {message.id}  {message.date} stop reading All: {all}  with text: {text}  accepted {take}", cl="pink")
                    break

                try:
                    if self.process_msg( message ) :  #define it in subclass !
                        take += 1
                        skip = "Taken +++"
                    else:
                        skip = "skipped..."

                    self.logInfo(f"History msg: {message.id}  {message.date}  All: {all}  with text: {text}  accepted {take}  {skip}")

                except Exception as e:
                    self.logError(f"Unexpected THistory exception {e=}, {type(e)=}")
                    self.logError(message.text)
                    self.logError( traceback.format_exc( 6, chain=True) )
                    
        # end cycle


async def telegram_main():
    Bot = THistory( "../Files/cfg-test.json")

    Bot.print_b( 'telegram_main', 'Start reading history' )

    await Bot.Start()

async def history_test():
    cfg_test = {
        'CfgFolder': "c:\\OneDrive\\Bot\\V2\\Devl\\Files\\",
        'OutFolder':  "UnDef-",
        
        "Section":  {
            'CfgFolder': "c:\\OneDrive\\Bot\\V2\\Devl\\Files\\",
            'OutFolder':  "UnDef-"
        }
    }

    jclass = T.CfgJson( cfg = cfg_test, section="Section" )
    
    Bot = THistory( jclass = jclass )

    await Bot.Start()

if __name__ == '__main__':
    asyncio.run(telegram_main())
