import asyncio, traceback

import appcfg as acfg, tools as T
from THistory import THistory

from sqliteSupport import Dbase, Table

class THistoryDb( THistory ):

    def dbTableInit(self, sectionTables ):
        # Tables init
        self.table = Table( sectionTables[0] )
      
    def dbTableOpen(self):
        self.table.Drop(self.db.cursor)
        self.table.Create(self.db.cursor)
        

    def dbTableClose(self):
        pass
#===========================================
    
    # add definition of db support
    def dbInit(self, jdata ):
        # init db; don't open!
        # jdata.cfg_section : "CfgFolder"+"DbFile"
        self.db = Dbase( jdata, jdata.cfg_section )
        if self.db.db_ready:
            tmp = self.section_cfg.get("Tables", None)

            if (tmp is not None and len(tmp) > 0):
                
                self.dbTableInit( tmp )
                
            else:
                self.db.db_ready = False
                self.logError(" Key Tables is not defined at ChannelA.__init__")

        self.db_initiated = False

    def dbOpen(self):
        if self.db.db_ready:
            # open db
            try:
                self.db.db_Open()
                
                self.dbTableOpen()

            except Exception as e:
                self.logError(' dbOpen Exception' + str(e) )
                self.logError(traceback.format_exc(4, chain=True))
                exit( -1 )
        else:
            self.logError(" db.db_ready = False in method dbOpen() ")
            exit(-2)

    def dbClose(self):
        if self.db.db_ready:
            
            self.dbTableClose()
            
            self.db.db_Close()

    # should be defined:
    def process_msg(self, msg):
        return False


    def __init__(self, cfg_file="cfg.json", section="Channel", jclass=None) -> None:
        super().__init__( cfg_file, section, jclass )


async def telegram_main():
    Bot = THistoryDb( acfg.cfg_files + "cfg-test.json")
    await Bot.Start()


if __name__ == '__main__':
    T.print_green('PyCharm')

    asyncio.run(telegram_main())
