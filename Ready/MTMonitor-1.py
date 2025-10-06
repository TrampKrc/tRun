
import sys, os
import signal, time, asyncio
from datetime import datetime as dt

RUN = False

# this is the Start script from Ready folder!
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Lib')))

import config as acfg
from  colorPrint import colorPrint as clp
import tools as T, gMessage as M
import TMonitor as tm, ExcMonitor as exm

def workThread_1( params ):
    # Start Telegram monitor
     asyncio.run( tm.start_TMonitor( params ) )

def workThread_2(params):
    # Start Exchange monitor
    asyncio.run( exm.start_Exchange( params ))

#
# Main entry point
#
async def main():

    global is_running

    # for manual stop
    def signal_handler( a, b ):
        global is_running

        print( f"Stop signal received ({a}  {b})." )
        is_running = False
        print( f" Stop after signal {is_running}")

    for name in (signal.SIGINT, signal.SIGTERM, signal.SIGABRT):
        signal.signal(name, signal_handler)

    mtm_cfg_file = acfg.cfg_files + "\\MTMonitor\\cfg-MTMonitor.json"
    logger = T.CfgJson( cfg_file = mtm_cfg_file, prefix = 'MTMonitor' )
    logger.openLog( lname='MTMonitor' )

    """
                    ----------->  TMonitor
                    |                |
              mainThread             |
                  |                  V
                  ------------->  EMonitor

    mainTread will control two workers:
    - worker-1: TMonitor, reads Telegram messages and puts data to queue for worker-2
    - worker-2: EMonitor, reads queue from worker-1 and sends orders to Exchange.
    The mainThread will control both workers and put CtrlMsg to queues.
    The workers will put CtrlMsg to mainThread queue.
    The mainThread will stop workers when CtrlMsg with status 'Exit' is received.
    The workers will stop when CtrlMsg with status 'Exit' is received.
    The mainThread will wait until all workers are stopped.
    The workers will put CtrlMsg to mainThread queue.
    
    """

    cq_get = M.xQueue()     # mainThread will get

    cq1_put = M.xQueue()    # mainThread will put to worker-1
    dq12_put = M.xQueue()   # worker-1 will put to worker-2:     w1 -> q -> w2
    dq12_get = M.xQueue()   # worker-1 will get from worker-2    w1 <- q <- w2

    cq2_put = M.xQueue()    # mainThread will put to worker-2

    if RUN:
        tout = 60*60*24
    else:
        tout = 60*5

    # parameters for monitoring Telegram.
    # Read msgs and put data to queue for ExchangeMonitor
    tmonitor_param = {
        "cfg_mem" : logger.cfg_all['TMonitor'],
        #"cfg_mem2" : copy.deepcopy( logger.cfg_all['TMonitor'] ),
        "section"  : "channelList",
        "tout": tout,
        "queues"   : [cq_get, cq1_put, dq12_put, dq12_get]
    }

    # parameters for monitoring Exchange
    # Read queue and send orders to Exchange Monitor
    emonitor_param = {
        "cfg_mem" : logger.cfg_all['EMonitor'],
        "section": None,
        "exc_keys": acfg.bybit_key_demo,
        "queues": [cq_get, cq2_put, dq12_put, dq12_get]
    }

    msgC1 = M.CtrlMsg('mainThread', 'TMonitor', body="Start")
    msgC2 = M.CtrlMsg('mainThread', 'ExcMonitor', body='Start"')

    cq1_put.async_put_nowait( msgC1.date() )
    cq2_put.async_put_nowait( msgC2.date() )

    coro_1 = asyncio.to_thread( workThread_1, tmonitor_param)
    #coro_2 = asyncio.to_thread(workThread_2, 'Start exchange control...', 10**5, queue = worker2)
    coro_2 = asyncio.to_thread( workThread_2, emonitor_param)

    all_tasks = set()
    all_tasks.add( asyncio.create_task( coro_1 ) )
    all_tasks.add( asyncio.create_task( coro_2 ) )

    # main loop
    logger.logInfo("mainThread:  Start monitoring ... ", cs=clp.cyan )
    is_running = True
    k = 0

    start = time.perf_counter()

    while is_running:
        if k % 100 == 0:
            clp.p_cyan( f"mainThread is working {k} sec input queue size = {cq_get.qsize()}" )
            #msgC2.body = "noGet"
            #cq2_put.async_put_nowait( msgC2.date() )

        k += 1

        #print(f' from main size= {queue.qsize()}')
        while cq_get.qsize() > 0:
            #print( T.yellow(f"mainThread ctrl input queue: { cq_get.qsize()}" ) )
            it = await cq_get.async_get()
            #print(f'{it["id"]}:\n  {it["msg"]}')
            logger.logInfo( "mainThread get msg from input queue:\n", it, cs=clp.cyan )
            # Notify the queue that the "work item" has been processed.
            cq_get.task_done()

            if type(it) == M.CtrlMsg and it.status == 'Exit':
                msgC2.body = "Stop"
                cq2_put.async_put_nowait( msgC2.date() )
                is_running = False

        await asyncio.sleep(1)

    # Cancel our worker tasks.
    logger.logInfo( "Canceling all tasks ... ", cs=clp.cyan )

    msgC1.status = 'Exit'
    cq1_put.async_put_nowait( msgC1.date() )

    msgC2.status = 'Exit'
    cq2_put.async_put_nowait( msgC2.date() )

    for task in all_tasks:
        task.cancel()

    logger.logInfo( "Wait until all worker tasks are cancelled.", cs=clp.cyan)
    rc = await asyncio.gather(*all_tasks, return_exceptions=True)
    print(rc[0], rc[1])

    end = time.perf_counter()
    logger.logInfo( f'It took {round(end - start, 0)} second(s) to complete.  Exit.' , cs=clp.cyan)

if __name__ == '__main__':
    asyncio.run( main() )


async def workThread_11(message, result=1000, delay=3, queue = None):

    ctrl_put = queue[1]
    ctrl_get = queue[0]

    data_put = queue[2]
    data_get = queue[3]

    is_running = True
    print(f"workThread_1:  start qu = { ctrl_get.qsize()} ")

    #loop = asyncio.new_event_loop()
    loop = asyncio.get_running_loop()
    print("----------------->", loop )
    #print("----------------->>", asyncio.get_running_loop())

    cfg_file = "c:/OneDrive/Bot/V2/Files/cfg-monitor-1.json"
    section = "Monitor"

    #thread = threading.current_thread()
    #print(f'name={thread.name}, daemon={thread.daemon}')

    task = None
    while is_running:
        print( T.blue( f"workThread_1: { time.time()} "))

        if not ctrl_get.empty():
            dd = ctrl_get.sync_get()
            print( "workThread_1 msg: ", dd )
            if "noGet" not in dd:
                print( T.blue( f"workThread_1:  noGet qu = {ctrl_get.qsize()} "))
                ctrl_get.task_done()

            if dd == "Start":
                # start
                #asyncio.run( tm.start_TMonitor( cfg_file, section, ctrl_get, data_put ) )
                task = asyncio.create_task( tm.start_TMonitor( cfg_file, section, ctrl_get, data_put ))
                #await qq
                #await tm.start_TMonitor( cfg_file, section, ctrl_get, data_put )
                print( "workThread_1:  Started")
                ctrl_put.async_put_nowait("workThread_1:  Started")

            elif dd == 'Stop':
                is_running = False
                ctrl_put.async_put_nowait("workThread_1:  stopped ")

        time.sleep(1)
    await task

    print(f"workThread_1:  End qu = { ctrl_get.qsize()} ")

def workThread_21(message, result=1000, delay=3, queue = None):
    ctrl_put = queue[0]
    ctrl_get = queue[1]

    data_put = queue[2]
    data_get = queue[3]

    is_running = True
    print(f"workThread_2:  start qu = {ctrl_get.qsize()} ")

    while is_running:
        print( T.pink( f"workThread_2: {dt.now()} "))

        if not ctrl_get.empty():
            dd = ctrl_get.sync_get()
            print(f" {dt.now()} workThread_2 ctrl_get msg:", dd)

            if "noGet" not in dd.body:
                print(T.pink( f"workThread_2:  noGet qu = {ctrl_get.qsize()}"))
                ctrl_get.task_done()

            if dd.body == "Start":
                # start
                ctrl_put.async_put_nowait("workThread_2:  Started")

            elif dd.body == 'Stop':
                is_running = False
                ctrl_put.async_put_nowait("workThread_2:  stopped ")
                break

        while not data_get.empty():
            dd = data_get.sync_get()
            print(f"{dt.now()} workThread_2 data msg:", dd)
            data_get.task_done()

        time.sleep(3)

    print(f"workThread_2:  End qu = {ctrl_get.qsize()} ")

    path = "c:\\OneDrive\\Bot\\V2\\Files\\"
    cfg_file = "cfg-h1.json"
    section = "ChannelH1"
    exc_keys = 'ByBitDemoAll'

    #exc.start_Exchange(path, cfg_file, section, exc_keys, queue)
    #asyncio.run( exc.astart_Exchange(path, cfg_file, section, exc_keys, queue) )

def work_20(message, result=1000, delay=3, queue=None):
    #q = Queue()

    time.sleep(45)
    print(f"work_2:  start qu = {queue.qsize()} ")
    while not queue.empty():
        dd = queue.get()
        print( "work_2: ", dd )
        queue.task_done()
        time.sleep(0.5)

    print("work_2:  return")
    return result
