
import os

if __name__ == '__main__':
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','Lib')))
    import config as acfg
else:
    import config as acfg

import asyncio
from   THistory import THistory
import tools as T, TMessage as M, p_table
#
# collect data in memory and print
#

class ReadHistoryMem( THistory ):
    
    def __init__(self, cfg_file="cfg.json", section="Channel", jclass=None, parser=None ) -> None:

        super().__init__( cfg_file=cfg_file, section=section, jclass=jclass, parser=parser )

        self.history_msgs = []
        self.all_msgs = []
    
    # msg processing; called from THistory->Run
    def process_msg(self, msg):
        # the msg is not empty and msg.date has been checked

        if self.section_cfg["UserId"] == 0 or self.section_cfg["UserId"] == msg.from_user.id:
            
            tdata = M.TMsg_Info(msg)

            self.all_msgs.append( tdata)

            # receive data from parser
            odata = self.channel_parser(self, msg)
            
            if odata is not None:
                self.history_msgs.append({'tdata': tdata, 'odata': odata})
                return True
        
        return False
    
    # all msgs are done ! call from THistory
    def Close(self):
        # Post-processing
        if len( self.history_msgs ) > 0:

            self.history_msgs.reverse()

            n = len( self.history_msgs )
            self.logInfo(f"Results: { n }", cl='yellow' )

            with open( os.path.join( self.base.out_folder, self.channel_cfg["HistoryFile"]), 'wt', encoding="utf-8") as fout:

                for data in self.history_msgs:
                    s = f" { data['tdata']._channel_msgId } {data['tdata']._channel_date} => { data['tdata'] } \n"
                    self.logInfo( s, cl='yellow' )

                    fout.write(f'==> {data['tdata']._channel_date } { data['tdata']._channel_utctime }\n'
                               f'teleg  msg:\n {data['tdata']}\n'
                               f'order data:\n {data['odata']}\n'
                               f'====================\n')

        self.save2File()

    def save2File(self):

        f_name = os.path.join( self.base.out_folder,  "All_" + self.channel_cfg["HistoryFile"] )

        self.logError("Save all messages to file: ", f_name)

        with open( f_name, 'wt', encoding="utf-8") as fout:
            for data in self.all_msgs:
                fout.write(f'==> {data._channel_date} {data._channel_utctime}\n'
                           f'teleg  msg:\n {data.Body}\n'
                           f'====================\n')


async def telegram_main():


    #section = "HistoryMem-CD"
    section = "HistoryMem-CAngel"


    cfg_file = os.path.join( acfg.cfg_files, "ReadHistoryMem.json")
    Bot = ReadHistoryMem( cfg_file, section, parser= p_table.parser_table['Template'])

    Bot.print_g( 'History ', cfg_file)
    await Bot.Start()

if __name__ == '__main__':

    asyncio.run( telegram_main() )
