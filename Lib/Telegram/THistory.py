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
    
    def dbClose(self):
        pass
        
    # should be defined:
    def process_msg(self, msg):
        return False

    """
    
    """
    
    def __init__(self, cfg_file="cfg.json", section="Channel", jclass=None, parser=None ) -> None:

        if jclass is not None:
            self.jdata = jclass
        else:
            self.jdata = T.CfgJson( cfg_file= cfg_file, section=section)

        super().__init__( self.jdata, section)

        channel_name = ""
        if parser is None:
            channel_name = self.channel_cfg.get("Name", None )
            if channel_name:
                self.channel_parser = pt.get( channel_name, None )
        else:
            self.channel_parser = parser

        if self.channel_parser is None:
            raise ValueError( f"Parser for channel {channel_name} Nof found cfg file: {cfg_file} ")

        self.dbInit( self.jdata )

    async def Start(self):
        self.dbOpen()
        await self.TClient_Start() # TClient_Start will call Run()

    # call from self.TClient_Start()
    async def Run(self):    # Read History
        self.logInfo(f"Read history: channelId {self.channel_cfg["Id"]} - {self.channel_cfg['Name']}")

        chat_id = self.section_cfg["Id"]
        limit  = self.section_cfg["HistoryLimit"]

        # convert to local timezone:
        local_tz = datetime.now().astimezone().tzinfo

        s_date = self.section_cfg["HistoryStart"]
        s_date_o = datetime.fromisoformat(s_date)
        s_date_l = s_date_o.astimezone(local_tz).strftime('%Y-%m-%d %H:%M:%S')

        e_date = self.section_cfg["HistoryEnd"]
        e_date_o = datetime.fromisoformat(e_date)
        e_date_l = e_date_o.astimezone(local_tz).strftime('%Y-%m-%d %H:%M:%S') #local date

        self.logInfo(f"Original Date interval: StartDate: {s_date} EndDate: {e_date} ")
        self.logInfo(f"Read channel history: StartDate: {s_date_l} EndDate: {e_date_l} Limit: {limit}")

        await  self.get_chanel_history_cycle( chat_id, s_date_l, dateEnd=e_date_l, limit=limit )

        # all events had been proceed; call self.Close()

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
