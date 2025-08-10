
import asyncio
import signal
import time
from datetime import datetime as dt

import appcfg as acfg

RUN = False # True

if RUN:

    prjRoot = ""

    import os, sys
    #current folder: DeplLib
    #root = os.path.dirname( os.path.dirname(os.path.abspath(__file__)) )
    root = os.path.dirname( os.path.abspath(__file__))
    #folder_up1 = os.path.dirname(folder0)
    sys.path.append( root + '/Tools')
    sys.path.append( root + '/Market')
    sys.path.append( root + '/Telegram')
    sys.path.append( 'D:/Cloud/OneDrive/Bot/V2/venv-vm-dev1/Lib/site-packages')

else:
    prjRoot = acfg.root_folder

import tools as T, gMessage as M, TMonitor as tm, ExcMonitor as exm

def workThread_1( params ):
     asyncio.run( tm.start_TMonitor( params ) )

def workThread_2(params):
    asyncio.run( exm.start_Exchange( params ))

async def main():

    global is_running

    def signal_handler( a, b ):
        global is_running

        print( f"Stop signal received ({a}  {b})." )
        is_running = False
        print( f" Stop after signal {is_running}")

    for name in (signal.SIGINT, signal.SIGTERM, signal.SIGABRT):
        signal.signal(name, signal_handler)

    start = time.perf_counter()
    is_running = True

    cq_get = M.xQueue()     # mainThread will get

    cq1_put = M.xQueue()    # mainThread will put to worker-1
    dq12_put = M.xQueue()   # worker-1 will put to worker-2
    dq12_get = M.xQueue()   # worker-1 will get from worker-2

    cq2_put = M.xQueue()    # mainThread will put to worker-2

    worker2 = [cq_get, cq2_put, dq12_get, dq12_put]

    all_tasks = set()
    #queue = Queue()

    if RUN:
        cfg_file = "D:\\BotLocal\\DepLib\\CfgFiles\\cfg-monitor-1.json"
        tout = 60*60*24
    else:
        cfg_file = acfg.cfg_files + "cfg-MTmonitor-1.json"
        tout = 60*5

    # parameters for monitoring Telegram.
    # Read msgs and put data to queue for ExchangeMonitor
    worker1_parm = {
        "cfg_file" : cfg_file,
        "section"  : "TMonitor",
        "tout": tout,
        "queues"   : [cq_get, cq1_put, dq12_put, dq12_get]
    }

    # parameters for monitoring Exchange
    # Read queue and send orders to Exchange Monitor
    worker2_parm = {
        "cfg_file" : cfg_file,
        "section": "EMonitor",
        "exc_keys": 'ByBitDemoAll',
        "queues": [cq_get, cq2_put, dq12_put, dq12_get]
    }

    msgC1 = M.CtrlMsg('mainThread', 'TMonitor', body="Start")
    msgC2 = M.CtrlMsg('mainThread', 'ExcMonitor', body='Start"')

    cq1_put.async_put_nowait( msgC1.date() )
    cq2_put.async_put_nowait( msgC2.date() )

    coro_1 = asyncio.to_thread( workThread_1, worker1_parm)
    #coro_2 = asyncio.to_thread(workThread_2, 'Start exchange control...', 10**5, queue = worker2)
    coro_2 = asyncio.to_thread( workThread_2, worker2_parm)

    all_tasks.add( asyncio.create_task( coro_1 ) )
    all_tasks.add( asyncio.create_task( coro_2 ) )

    # main loop
    k = 0
    while is_running:
        if k % 100 == 0:
            print( T.yellow( f"mainThread is working {k} sec  q1 = {cq_get.qsize()}") )
            #msgC2.body = "noGet"
            #cq2_put.async_put_nowait( msgC2.date() )

        k += 1

        #print(f' from main size= {queue.qsize()}')
        while cq_get.qsize() > 0:
            #print( T.yellow(f"mainThread ctrl input queue: { cq_get.qsize()}" ) )
            it = await cq_get.async_get()
            #print(f'{it["id"]}:\n  {it["msg"]}')
            print( T.yellow("mainThread get:\n"), T.yellow(it) )
            # Notify the queue that the "work item" has been processed.
            cq_get.task_done()

            if type(it) == M.CtrlMsg and it.status == 'Exit':
                msgC2.body = "Stop"
                cq2_put.async_put_nowait( msgC2.date() )
                is_running = False

        await asyncio.sleep(1)

    # Cancel our worker tasks.
    print( T.yellow("Canceling all tasks ... " ))

    msgC1.status = 'Exit'
    cq1_put.async_put_nowait( msgC1.date() )

    msgC2.status = 'Exit'
    cq2_put.async_put_nowait( msgC2.date() )

    for task in all_tasks:
        task.cancel()

    print( T.yellow("Wait until all worker tasks are cancelled.") )
    rc = await asyncio.gather(*all_tasks, return_exceptions=True)
    print(rc[0], rc[1])

    end = time.perf_counter()
    print(f'It took {round(end - start, 0)} second(s) to complete.')

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
