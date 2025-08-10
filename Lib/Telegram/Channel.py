

class TChannel():

    Tclient: Client

    is_running: bool

    lock: asyncio.Lock
    log: logging.Logger
    loop: asyncio.AbstractEventLoop
    stop_manual: bool
    stopping: bool

    def __init__(self, cfg_file="cfg.json" ) -> None:

        super().__init__( cfg_file )


    def filter(self, msg):
        print(tools.yellow('Filter0'))
        return True

    def parser(self, msg):
        print(tools.yellow('Parser0'))
        return msg
