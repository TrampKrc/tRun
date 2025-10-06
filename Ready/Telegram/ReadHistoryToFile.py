
import os
import asyncio

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','Lib')))

import config as acfg, tools as T
from   THistory import THistory
import TMessage as M
#
# collect data in memory and print
#

class ReadHistoryMem( THistory ):
    
    def __init__(self, cfg_file="cfg.json", section="ChannelList", jclass=None ) -> None:

        super().__init__( cfg_file=cfg_file, section=section, jclass=jclass )

    def startChannel(self):
        self.signal_msgs = []
        self.all_msgs = []

    # msg processing; called from THistory->Run
    def process_msg(self, msg):
        # the msg is not empty and msg.date has been checked

        if self.cfg_channel_desc.get("UserId",0) == 0 or self.cfg_channel_desc["UserId"] == msg.from_user.id:

            tdata = M.TMsg_Info( msg )

            self.all_msgs.append( tdata )

            # receive data from parser
            odata = self.channel_parser(self, msg)
            
            if odata is not None:
                self.signal_msgs.append({'tdata': tdata, 'odata': odata})
                return True
        
        return False

    def closeChannel(self):

        # channel Post-processing
        ext = T.str_DateTime("-%m%d%Y-%H%M%S.txt")

        n_signal = len(self.signal_msgs)
        if n_signal > 0:
            self.logInfo(f"Signal Messages: { n_signal }", cl='yellow' )
            self.signal_msgs.reverse()

            file_name = self.cfg_channel_desc.get("SignalMsgFile", "SignalMsg-") + self.cfg_channel_desc['Name'] + ext
            f_name = os.path.join( self.base.out_folder,  file_name )
            self.logInfo("Save signal messages to file: ", f_name, cl='green2')

            with open( f_name, 'wt', encoding="utf-8") as fout:

                for data in self.signal_msgs:
                    s = f" { data['tdata']._channel_msgId } {data['tdata']._channel_date} => { data['tdata'] }"
                    self.logInfo( s, cl='yellow' )

                    fout.write(f'==> {data['tdata']._channel_date } { data['tdata']._channel_utctime }\n'
                               f'teleg  msg:\n {data['tdata']}\n'
                               f'order data:\n {data['odata']}\n'
                               f'====================\n')

        #self.save2File()

        n_all = len(self.all_msgs)

        if n_all > 0:
            self.logInfo(f"All Messages: { n_all }", cl='yellow' )
            self.all_msgs.reverse()

            file_name = self.cfg_channel_desc.get("AllMsgFile", "AllMsg-") + self.cfg_channel_desc['Name'] + ext
            f_name = os.path.join( self.base.out_folder,  file_name )
            self.logInfo("Save all messages to file: ", f_name, cl='green2')

            with open( f_name, 'wt', encoding="utf-8") as fout:
                for data in self.all_msgs:
                    fout.write(f'==> {data._channel_date} {data._channel_utctime}\n'
                               f'teleg  msg:\n {data.Body}\n'
                               f'====================\n')

    # all msgs are done ! call from THistory
    def Close(self):
        super().Close()

    def save2File(self):

        f_name = os.path.join( self.base.out_folder,  "All-" + self.channel_cfg["HistoryFile"] )

        self.logError("Save all messages to file: ", f_name)

        with open( f_name, 'wt', encoding="utf-8") as fout:
            for data in self.all_msgs:
                fout.write(f'==> {data._channel_date} {data._channel_utctime}\n'
                           f'teleg  msg:\n {data.Body}\n'
                           f'====================\n')


async def telegram_main():

    section = "ChannelList-001" # section with the list of channels names
    cfg_file = os.path.join( acfg.cfg_files, "ReadHistoryFiles/cfg_ReadChannels.json")

    Bot = ReadHistoryMem( cfg_file, section )

    #Bot.print_g( 'History ', cfg_file)
    await Bot.Start()

if __name__ == '__main__':

    asyncio.run( telegram_main() )
