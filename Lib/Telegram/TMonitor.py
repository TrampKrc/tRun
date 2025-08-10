
import sys, asyncio
import copy

import appcfg as acfg
import tools as T, gMessage as M, utils as U
from Parser import parsers_old as P
from   TClient import TClient

from pyrogram import filters
from pyrogram.handlers import MessageHandler

class TMonitor( TClient ):

    #def __init__(self, cfg_file="cfg.json", section="Channel", jclass=None, ctrl_q= None, out_q = None) -> None:
    def __init__(self, cfg_file="cfg.json", section="Channel", jclass=None, queues = None) -> None:

        if jclass is not None:
            jdata = jclass
            jdata.prefix = "TMonitor"
        else:
            jdata = T.CfgJson( cfg_file= cfg_file, section=section, lname='TMonitor', prefix='TMonitor')

        super().__init__( jdata, section )

        if queues is not None:
            self.q_ctrl_out   = queues[0]  # put a ctrl msg
            self.q_ctrl_input = queues[1]  # get a ctrl msg
            self.q_out        = queues[2]  # put a data to another worker thread ( Exchange )
        else:
            self.q_ctrl_out   = M.xQueue()  # put a ctrl msg
            self.q_ctrl_input = M.xQueue()  # get a ctrl msg
            self.q_out        = M.xQueue()  # put a data to another worker thread ( Exchange )

        self.q_handler = M.xQueue() # get data from msg handlers

        self.channel_cfg["Id"] = -1

# ----------- configure ------------------

        self.channelTest = {
            'YK_S1':  { 'id': -1001400228409, 'parser': P.process_channel_S1 },
            'YK-Sig': { 'id': -1001754270660, 'parser': P.process_channel_Sig }
        }
        #'Криптонец': -1001514172889,
        #'Криптонец': -1001768035392,
        #'Криптонец': -1001266391544,

        self.channel = {
            'Мастерство трейдинга': { 'id': -1001500911313, 'parser': P.process_master_trading },
            'Crypto Daniel':        { 'id': -1001633253042, 'parser': P.process_crypto_daniel },
            'Trade Indicator 🚀':   { 'id': -1001869173929, 'parser': P.process_trade_indicator },
            'Криптонец':            { 'id': -1001768035392, 'parser': P.process_cryptonec },

            'Cornix Notifications': { 'id':  605763187,     'parser': P.process_channel_cornix }
        }

        #self.filter_test = filters.chat( self.channelTest['YK_S1']['id']) | filters.chat( self.channelTest['YK-Sig']['id'])
        self.filter_test = filters.chat( [ self.channelTest['YK_S1']['id'], self.channelTest['YK-Sig']['id'] ])

        #self.filter_work = filters.chat( self.chan['Мастерство трейдинга'] ) |\
        #                   filters.chat( self.chan['Crypto Daniel'] ) |\
        #                   filters.chat( self.chan['Криптонец'] ) |\
        #                   filters.chat( self.chan['Cornix Notifications'] )

        self.filter_work = filters.chat( [ it['id'] for it in self.channel.values() ])

        self.msgC = M.CtrlMsg('TMonitor', 'mainThread')
        self.msgE = M.CtrlMsg('TMonitor', 'Thread-2')

    async def Start(self, tout=None ):

        #self.q_ctrl = ctrl_q if ctrl_q is not None else self.q_ctrl
        #self.q_out = out_q if out_q is not None else self.q_out
        self.tout = tout

        await self.TClient_Start() # TClient_Start will call Run()

    # call from self.TClient_Start()
    async def Run(self):
#        thread = threading.current_thread()
#        print(f'name={thread.name}, daemon={thread.daemon}')
#        loop = asyncio.get_running_loop()

        if self.tout == 0:
            if( limit := self.channel_cfg.get( "MonitorMinutes", None ) is not None ):
                self.tout = limit * 60

        if self.tout > 0:
            check_timer = asyncio.create_task(U.task_timer( self.tout, period=3600 ))

        self.msgC.body = "TMonitor initiates handlers"
        print(T.blue( 'Cmsg= ', self.msgC.date() ))
        #self.q_ctrl_out.async_put_nowait(copy.deepcopy(msgX))
        self.q_ctrl_out.async_put_nowait( self.msgC )

        self.setup_handlers()

        self.msgC.body = "TMonitor: handlers are started"
        print(T.blue( 'msgC= ', self.msgC.date() ) )
        self.q_ctrl_out.async_put_nowait(self.msgC)

        self.logInfo("Started", c=T.cyan)
        self.logInfo(f"Channels: { self.channel.keys() }")

        # main loop
        self.is_running = True
        k = 0
        while self.is_running and ( True if self.tout == 0 else check_timer.done() == False  ): # and check_timer.done() == False:

            if k % 100 == 0:
                self.logInfo( f"Handlers are working.... {k} sec", c=T.cyan )
                self.msgC.body = f' TMonitor ==> to Main: TMonitor are working.... {k} sec'
                self.q_ctrl_out.async_put_nowait( copy.deepcopy(self.msgC.date()) )
                #print(T.blue("Msg to Main sent"))

                self.msgE.status = 'Info'
                self.msgE.body = f'TMonitor ==> to Thread2: TMonitor running {k} sec'
                self.q_out.async_put_nowait(self.msgE.date())
                #print(T.blue("Msg to Thread2 sent"))

            # check queue from Main Monitor:
            while not self.q_ctrl_input.empty():
                msgQ = await self.q_ctrl_input.async_get()
                print( T.blue("TMonitor: From Q_CTRL: "), T.blue(msgQ ) )
                self.q_ctrl_input.task_done()

                if msgQ.status == 'Exit':
                    self.is_running = False

            # check queue from handlers:
            while not self.q_handler.empty():
                msgM = await self.q_handler.async_get() # got parserMsg
                #print( T.blue("from Handler queue: "), T.blue(msgM) )
                self.q_handler.task_done()

                # put msg to exchange monitor
                self.msgE.status = 'Order'
                self.msgE.body = msgM
                self.q_out.async_put_nowait(self.msgE.date())
                print(T.blue("Msg to Thread2 sent"))

                # notify Main monitor:
                #self.msgC.body = msgM
                #self.q_ctrl_out.async_put_nowait( self.msgC )
                #print(T.blue("Msg to Main sent"))

            #self.queue.put_nowait( datetime.time() )
            await asyncio.sleep(1)
            k += 1

        # exit from Run
        self.logInfo("TMonitor Stopped")

        self.msgC.status = 'Exit'
        self.msgC.body   = f'TMonitor exit after {k} sec'
        self.q_ctrl_out.async_put_nowait( self.msgC.date() )

        return

    def setup_handlers(self):
        '''
        # my_handler = MessageHandler(my_function)
        # app.add_handler(my_handler)
        # app.add_handler( MessageHandler( my_function2, filters.sticker & (filters.channel | filters.private)))
        # filters.sticker | filters.regex("pyrogram")
        '''

        #self.lock1 = asyncio.Lock()
        self.Tclient.add_handler(MessageHandler( self.msg_handler_test, self.filter_test ))
        #self.lock1.release()

        #self.lock2 = asyncio.Lock()
        self.Tclient.add_handler(MessageHandler( self.msg_handler_work, self.filter_work ))
        #self.lock2.release()

        print(T.green("Messages handlers is set up"))

    async def msg_handler_test(self, client, msg):
        self.logInfo(f"Msg TestHandler got new msg from {msg.chat.title}: " + T.green(msg.date), ':\n', P.msg_text(msg) )

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
        self.logInfo(f"Msg WorkHandler got new msg from {msg.chat.title}: msg.date={msg.date} :\n", P.msg_text(msg) )

        if self.choose_channel( msg ):
            self.logInfo( f"Msg WorkHandler end; mds.date: {msg.date}", c=T.green)
        else:
            self.logInfo( f"Msg WorkHandler end. no processing {msg.date}", c=T.red)

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
            self.logInfo("ChooseChannel put msg to exchange queue\n" + t_ )

            with open(self.jc.filename+'.txt', 'w+', encoding='utf-8') as f:
                f.write( t_ )
                f.flush()

            # put to Queue for TMonitor main thread
            self.q_handler.async_put_nowait( pMsg )
            return True
        else:
            self.logInfo(f'ChooseChannel: {msg.chat.title}: Parser returns Nothing' )

        return False

async def start_TMonitor( p, jclass = None ):
    # cfg_file="cfg.json", section="Channel", jclass=None, ctrl_q= None, out_q = None) -> None:

    Bot = TMonitor( p['cfg_file'], p['section'], jclass, p['queues'] )
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

    param = {
        "cfg_file" : acfg.cfg_files + "cfg-MTmonitor-1.json",
        "section"  : "TMonitor",
        "tout": 300,
        "queues"   : [cq_get, cq1_put, dq12_put, dq12_get]
    }
    await start_TMonitor( param )

if __name__ == '__main__':
    asyncio.run( test_TMonitor() )


