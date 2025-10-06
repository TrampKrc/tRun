from enum import Enum
from dataclasses import dataclass
from datetime import datetime as dt, timezone

class OrderAct(Enum):
    Long = 1
    Short = -1

class OrderSide(Enum):
    Open  = 1
    Close = -1

class OrderType(Enum):
    Market = "market"
    Limit = "limit"
    Stop = "stop"
    Info = "info"

class OrderStatus(Enum):
    Created = "created"
    Pending = "pending"
    Filled = "filled"
    Cancelled = "cancelled"
    Rejected = "rejected"

@dataclass
class TMsg_Info:
    _channel: str = None        # 1 parameter -> telegram msg
    _channel_from: str = None   # 2 parameter
    _channel_msgId: str = ""
    _channel_date: dt = None
    _channel_utctime: dt = None
    _channel_timestamp: str = ""
    _sessionId: str = ""
    _session_msgId: str = ""
    _body: str = None

    def __post_init__( self ):
        msg_param1 = self._channel
        if msg_param1 :
            self._set( msg_param1 )


    def _set(self, t_msg):

        self._channel = t_msg.chat.title
        self._channel_msgId = t_msg.id
        self._channel_date = t_msg.date.astimezone( dt.now().astimezone().tzinfo )
        self._channel_utc_timestamp = t_msg.date.astimezone(timezone.utc).timestamp()
        self.setBody( t_msg )

    @property
    def Body(self):
        return self._body

    def setBody(self, msg):
        text = "" if msg.caption == None else msg.caption
        text += "" if msg.text == None else msg.text
        text = "".join(text).replace("\n", " ")
        self._body = text

@dataclass
class Order_Info:
    utc_now: dt = None
    entry_utc_timestamp: int = 0

    symbol: str = "" # BTC/USDT
    order_act: OrderAct = OrderAct.Long    # Long/Short
    order_type: OrderType = OrderType.Limit  # market/limit/info
    order_side: OrderSide = OrderSide.Open   # open 1 / close -1

    entry_price: list = None  # price_min, price_max
    entry_base_size: float = 0  # usdt before leverage
    entry_coin_size: float = 0  # BTC
    entry_leverage: int = 10  # multipluer
    entry_leverage_type: int = 0   # cross(0)/isoleited(1)

    tpPrice: list = None    # [ [price,%position], [price,%pos] ]
    slPrice: list = None    # [ stop_loss_price, additional_info]
    size: float = 0

    comment: str = ""
    status = OrderStatus.Rejected
    #err_flag = False

    def __post_init__(self):
        if self.entry_price is None:
            self.entry_price = []

        if self.tpPrice is None:
            self.tpPrice = []

        if self.slPrice is None:
            self.slPrice = [0]

        self.utc_now = dt.now().astimezone(timezone.utc)

    def setOrderType(self, type: str ):

        match type.lower():
            case 'market':
                self.order_type = OrderType.Market

            case 'limit':
                self.order_type = OrderType.Limit

            case 'stop':
                self.order_type = OrderType.Stop

            case _:
                self.order_type = OrderType.Info

    def setOrderSide(self, side: str):

        match side.lower():
            case 'open':
                self.order_side = OrderSide.Open

            case 'close':
                self.order_side = OrderSide.Close

            case _:
                self.order_side = 0

    def setOrderAct(self, direction: str ):
        act = direction.lower()
        if act in ['buy', 'long', 'лонг']:
            self.order_act = OrderAct.Long
        elif act in ['sell', 'short', 'шорт']:
            self.order_act = OrderAct.Short
        else:
            # Set side to 0 for unrecognized directions
            self.order_side = 0

    def is_buy(self):
        return self.order_act == OrderAct.Long

    def p_str(self):

        if self.order_type == OrderType.Info:
            return f" symbol:{self.symbol} \n text:{self.comment}\n"

        else:
            return f"\nsymbol:{self.symbol} \n\
    action:{self.order_act}, order_type:{self.order_type}, order_side:{self.order_side}, \n\
    entry_price:{self.entry_price}  leverage:{self.entry_leverage}\n\
    entry_base_size:{self.entry_base_size}    entry_coin_size:{self.entry_coin_size}\n\
    tpPrice:{self.tpPrice}\n\
    slPrice:{self.slPrice}\n"

if __name__ == '__main__':
    # Test the Order_Info class
    m = Order_Info()
    print(f"Order direction: {m.order_act}")
    print(f"Order type: {m.order_type}")
    print(f"UTC now: {m.utc_now}")

    # Test setting order type
    m.setOrderType("market")
    print(f"After setOrderType('market'), order_type: {m.order_type}")

    # Test setting direction
    m.setOrderAct("short")
    print(f"After setDirection('short'), direction: {m.order_act}")
    print(f"Is buy: {m.is_buy()}")

    # Test string representation
    print("String representation:")
    print(m.p_str())

    # Test TMsg_Info class
    print("\nTMsg_Info cannot be fully tested without a telegram message object")
