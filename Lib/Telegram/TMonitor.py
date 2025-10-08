
import copy

import os
import asyncio

from pyrogram import filters
from pyrogram.handlers import MessageHandler

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config as acfg
import tools as T, gMessage as M, utils as U
from  TClient import TClient
from  p_table import parser_table
from colorPrint import colorPrint as clp

class TMonitor( TClient ):

    def __init__(self, cfg_data, channelList="channelList", queues = None) -> None:

        super().__init__( cfg_data )

        if queues is not None:
            self.q_ctrl_out   = queues[0]  # put a ctrl msg
            self.q_ctrl_input = queues[1]  # get a ctrl msg
            self.q_out        = queues[2]  # put a data to another worker thread ( Exchange )
        else:
            self.q_ctrl_out   = M.xQueue()  # put a ctrl msg
            self.q_ctrl_input = M.xQueue()  # get a ctrl msg
            self.q_out        = M.xQueue()  # put a data to another worker thread ( Exchange )

        self.q_handler = M.xQueue() # get data from msg handlers

# ----------- configure ------------------

        self.OrderFile = self.cfg_all.get("OrderFile", None)
        if self.OrderFile:
            self.OrderFile = self.OrderFile + T.str_DateTime("-%m%d%Y-%H%M%S") + ".txt"
            self.OrderFile = os.path.join( acfg.out_files, self.OrderFile )
            self.logInfo(f"File to save orders: {self.OrderFile}", cl='green2')

        # channelList  # name of section with list of channels for processing
        channels = self.cfg_all.get( channelList, None )
        if channels is None:
            raise ValueError("No section <%s> in config data: \n %s" % (channelList, self.cfg_all) )

        # skip entries that starts with '-'
        self.channel_dict = dict( (name, {'id':id, 'parser':None })  for name, id in channels.items() if name[0] != '-')
        if len( self.channel_dict ) == 0:
            raise ValueError("No channel names found in config file. Check section <%s>: \n %s" % (channelList, self.all_cfg) )

# -------- channel parsers ----------------
        for name, value in self.channel_dict.items():
            value['parser'] = parser_table.get(name, parser_table['EmptyParser'])

    async def Start(self, tout=None ):

        #self.q_ctrl = ctrl_q if ctrl_q is not None else self.q_ctrl
        #self.q_out = out_q if out_q is not None else self.q_out
        self.tout = tout

        await self.TClient_Start() # TClient_Start will call Run()

    async def Run(self):
        #       check channels id:
        channels_check = [name for name, val in self.channel_dict.items() if val['id'] == 0]
        # we have something to check
        if len(channels_check) > 0:
            channel_ids = await self.find_channel_ids(filter=channels_check)

            if len(channel_ids) > 0:
                for name, id in channel_ids.items():
                    self.channel_dict[name]['id'] = id
                    self.logInfo(f"Channel {name} id is set to {id}", cl='green')

            # nothing was found. all channels have id = 0
            elif len(channels_check) == len(self.channel_dict):
                raise Exception("No channel Ids were found")

            # cleanup channels that still have id = 0
            for name in channels_check:
                if self.channel_dict[name]['id'] == 0:
                    self.logError(f"Channel {name} id is not found in Telegram. Check the name or Id.")
                    del self.channel_dict[name]

        self.logInfo(f"The list of channels to catch:\n",
                     [(name, val['id']) for name, val in self.channel_dict.items()], cl='green')

        self.filter_work = filters.chat([it['id'] for it in self.channel_dict.values()])

        # self.filter_test = filters.chat( [ self.channelTest['YK_S1']['id'], self.channelTest['YK-Sig']['id'] ])
        """
        #self.filter_work = filters.chat( self.chan['Мастерство трейдинга'] ) |\
        #                   filters.chat( self.chan['Crypto Daniel'] ) |\
        #                   filters.chat( self.chan['Криптонец'] ) |\
        #                   filters.chat( self.chan['Cornix Notifications'] )
        """

        self.msgC = M.CtrlMsg('TMonitor', 'mainThread')
        self.msgE = M.CtrlMsg('TMonitor', 'ExcMonitor')

        self.msgC.body = "TMonitor initiates handlers"
        self.logInfo('Cmsg= ', self.msgC.date(), cl='green')

        # self.q_ctrl_out.async_put_nowait(copy.deepcopy(msgX))
        self.q_ctrl_out.async_put_nowait(self.msgC)

        self.setup_handlers()

        self.msgC.body = "TMonitor: handlers are started"
        self.logInfo('msgC= ', self.msgC.date(), cs=clp.green)
        self.q_ctrl_out.async_put_nowait(self.msgC)

        self.logInfo("Started", cs=clp.green )
        self.logInfo(f"Channels: {self.channel_dict.keys()}", cs=clp.green )

        # main loop
        await self.main_loop()

        # exit from Run
        self.logInfo("TMonitor Stopped", cl='green2')

        self.msgC.status = 'Exit'
        # self.msgC.body   = f'TMonitor exit after {k} sec'
        self.q_ctrl_out.async_put_nowait(self.msgC.date())

        return

    async def main_loop(self):

        if self.tout == 0:
            if( limit := self.channel_cfg.get( "MonitorHours", None ) is not None ):
                self.tout = int( limit * 60 * 60 )

        if self.tout > 0:
            check_timer = asyncio.create_task(U.task_timer( self.tout, period=3600 ))

        self.is_running = True
        k = 0
        while self.is_running and ( True if self.tout == 0 else check_timer.done() == False  ): # and check_timer.done() == False:

            if k % 100 == 0:
                self.logInfo( f"Handlers are working.... {k} sec", cl='green' )
                self.msgC.body = f' TMonitor ==> to Main: TMonitor are working.... {k} sec'
                self.q_ctrl_out.async_put_nowait( copy.deepcopy(self.msgC.date()) )
                #print(T.blue("Msg to Main sent"))

                self.msgE.status = 'Info'
                self.msgE.body = f'TMonitor ==> to ExcMonitor: TMonitor running {k} sec'
                self.q_out.async_put_nowait(self.msgE.date())
                #print(T.blue("Msg to Thread2 sent"))

            # check queue from Main Monitor:
            await self.check_mainMonitor_queue()

            # check queue from msg handlers:
            await self.check_msgHandler_queue()

            #self.queue.put_nowait( datetime.time() )
            await asyncio.sleep(1)
            k += 1

    async def check_mainMonitor_queue(self):
        while not self.q_ctrl_input.empty():
            msgQ = await self.q_ctrl_input.async_get()
            self.logInfo("TMonitor: From Q_CTRL: ", msgQ, cs=clp.green)
            self.q_ctrl_input.task_done()

            if msgQ.status == 'Exit':
                self.is_running = False

    async def check_msgHandler_queue(self):
        while not self.q_handler.empty():
            msgM = await self.q_handler.async_get()  # got TMessage.Order_Info class
            self.logInfo("from msg Handler queue: ", msgM, cs=clp.green)
            self.q_handler.task_done()

            # put msg to exchange monitor
            self.msgE.status = 'Order'
            self.msgE.body = msgM
            self.q_out.async_put_nowait(self.msgE.date())
            self.logInfo("TMonitor -> ExcMonitor: Msg to Exchange Monitor sent", cs=clp.green)

            # notify Main monitor:
            # self.msgC.body = msgM
            # self.q_ctrl_out.async_put_nowait( self.msgC )
            # print(T.blue("Msg to Main sent"))


    # called from self.TClient_Start()

    def setup_handlers(self):
        '''
        # my_handler = MessageHandler(my_function)
        # app.add_handler(my_handler)
        # app.add_handler( MessageHandler( my_function2, filters.sticker & (filters.channel | filters.private)))
        # filters.sticker | filters.regex("pyrogram")
        '''

        #self.lock1 = asyncio.Lock()
        #self.Tclient.add_handler(MessageHandler( self.msg_handler_test, self.filter_test ))
        #self.lock1.release()

        #self.lock2 = asyncio.Lock()
        self.Tclient.add_handler(MessageHandler( self.msg_handler_work, self.filter_work ))
        #self.lock2.release()

        self.logInfo( "Messages handlers is set up", cl='green')

    async def msg_handler_test(self, client, msg):
        self.logInfo(f"Msg TestHandler got new msg from {msg.chat.title}: " + clp.cl_text(msg.date, cs=clp.green), ':\n' ) #, P.msg_text(msg) )

        call_parser = self.channelTest.get( msg.chat.title, None )
        if call_parser is None:
            self.logError(f"Msg TestHandler: Channel {msg.chat.title} is not supported ")
            return False

        try:
            # to emulate real msg processing -> msg.chat.title = real channel name
            rc = call_parser['parser']( self, msg )
        except:
            self.logError( 'Msg TestHandler: Test Parser Error:\n%s' % ( sys.exc_info()[1]))
            rc = None

        if rc is not None and self.choose_channel( msg ):
            print( T.green( f"Msg TestHandler end; mds.date: {msg.date}"))

        # forward to me as alarm
        #    await msg.forward("me")
        # await self.Tclient.forward_message("me", self.chn["Id"], msg.id)
        # copy() so there's no "forwarded from" header
        # message.copy(chat_id=OUTPUT__MT_FORWARD_CHAT_ID,  caption="")

    async def msg_handler_work(self, client, msg):
        self.logInfo(f"Msg WorkHandler got new msg from {msg.chat.title}: msg.date={msg.date} :\n", cs=clp.green) #, P.msg_text(msg) )

        try:
            # call dynamic parser:
            # orderInfo <- TMessage.Order_Info; no data about channel.

            orderInfo= self.channel_dict[ msg.chat.title ]['parser']( self, msg )

        except:
            self.logError( 'Parser Error:\n%s' % ( sys.exc_info()[1]))
            orderInfo = None

        if orderInfo is not None:

            try:
                t_ = orderInfo.p_str()
                self.logInfo("Put order to exchange queue:\n" + t_, cs=clp.green )

                if self.OrderFile:
                    with open(self.OrderFile, 'a+', encoding='utf-8') as f:
                        f.write( f"From channel: {msg.chat.title}")
                        f.write( t_ + '\n')
                        f.flush()

                # put to Order to Queue for TMonitor main thread
                # now we need wrapper to include channel/msg info ?
                self.q_handler.async_put_nowait( orderInfo )
            except:
                self.logError('Error while putting msg to queue for EMonitor:\n%s' % (sys.exc_info()[1]))

            self.logInfo( f"Msg WorkHandler end; mds.date: {msg.date}", cs=clp.green)

        else:
            self.logInfo(f'ChooseChannel: {msg.chat.title}: Parser returns Nothing', cs=clp.green )
            self.logInfo( f"Msg WorkHandler end. no processing {msg.date}", cs=clp.green2)


    def choose_channel(self, msg ):

        call_parser = self.channel.get( msg.chat.title, None )
        if call_parser is None:
            self.logError(f"Channel {msg.chat.title} is not supported ")
            return False

        try:
            pMsg = call_parser['parser']( self, msg )
        except:
            self.logError( 'Parser Error:\n%s' % ( sys.exc_info()[1]))
            pMsg = None

        if pMsg is not None:

            #s = self.jc.logInfo("Parser. put msg to queue", pMsg.__dict__())
            #self.jc.logInfo("Parser. put msg to queue" + pMsg.__dict__())
            t_ = pMsg.str()
            self.logInfo("ChooseChannel put msg to exchange queue\n" + t_, cs=clp.green )

            with open(self.jc.filename+'.txt', 'w+', encoding='utf-8') as f:
                f.write( t_ )
                f.flush()

            # put to Queue for TMonitor main thread
            self.q_handler.async_put_nowait( pMsg )
            return True
        else:
            self.logInfo(f'ChooseChannel: {msg.chat.title}: Parser returns Nothing', cs=clp.green2 )

        return False

# --------- start TMonitor in async mode ----------------
async def start_TMonitor( p ):

    cfg_data = T.CfgJson( cfg_mem= p['cfg_mem'], section=p['section'], prefix='TMonitor')
    cfg_data.openLog(lname='TMonitor')

    Bot = TMonitor( cfg_data, p['section'], p['queues'] )

    msg = {
        'Thread':'TMonitor',
        'Status':'Info',
        'Body': 'Monitor initiated'
    }
    p['queues'][0].async_put_nowait(msg)

    await Bot.Start( tout = p['tout'] )


async def test_TMonitor():
    cq_get = M.xQueue()     # monitor will put
    cq1_put = M.xQueue()    # monitor will get
    dq12_put = M.xQueue()   # monitor will put data for  exchange thread
    dq12_get = M.xQueue()   # monitor will get data from exchange thread

    cfg_data = T.CfgJson( acfg.cfg_files + "\\cfg-Tmonitor.json")

    param = {
        "cfg_mem" : cfg_data.cfg_all,
        "section"  : "channelList",
        "tout": 150,
        "queues"   : [cq_get, cq1_put, dq12_put, dq12_get]
    }
    await start_TMonitor( param )

if __name__ == '__main__':
    asyncio.run( test_TMonitor() )


