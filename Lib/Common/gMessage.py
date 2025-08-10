import asyncio

from datetime import datetime as dt, timezone

class body:
    def __init__(self):
        self.sym = ""
        self.side = ""
        self.type = ""
        self.size = 0
        self.lever = 0
        self.direction = 0
        self.openPrice = []
        self.tpPrice = []
        self.slPrice = []

class qMsg( object ):
    def __init__(self, type=1 ):
        self._type = type
        self._time = ""
        self._channal = ""
        self._channal_msgId = ""
        self._channal_timestamp = ""
        self._sessionId = ""
        self._session_msgId = ""
        self._body = body() if type == 1 else None


class CtrlMsg(object):
    def __init__(self, who, where, status='Info', body="" ):
        self.who = who
        self.where = where
        self.status = status
        self.body = body
        self.mdate = None

    def date(self):
        self.mdate = dt.now()
        return self

    def str(self):
        return f' Ctrlmsg Date={self.mdate} who={self.who} => {self.where}; status={self.status} body=\n{self.body}'

    def __str__(self):
        return self.str()

class xQueue:
    def __init__(self):
        self._loop = asyncio.get_running_loop()
        self._queue = asyncio.Queue()

    def sync_put_nowait(self, item):
        self._loop.call_soon(self._queue.put_nowait, item)

    def sync_put(self, item):
        asyncio.run_coroutine_threadsafe(self._queue.put(item), self._loop).result()

    def sync_get(self):
        return asyncio.run_coroutine_threadsafe(self._queue.get(), self._loop).result()

    def async_put_nowait(self, item):
        self._queue.put_nowait(item)

    async def async_put(self, item):
        await self._queue.put(item)

    async def async_get(self):
        return await self._queue.get()

    def nowait_get(self):
        return self._queue.get_nowait()

    def empty(self):
        return  self._queue.empty()

    def qsize(self):
        return  self._queue.qsize()

    def task_done(self):
        return  self._queue.task_done()
