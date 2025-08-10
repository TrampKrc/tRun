# -*- coding: utf-8 -*-
import os
import sys

import tools as T, utils as U

#from binance_exchange import binance_Exchange
from yk_bybit import yk_Bybit_demo

#from bybit_exchange_pro import bybit_Exchange_pro

"""
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')
import ccxt  # noqa: E402
from pprint import pprint
print('CCXT Version:', ccxt.__version__)
exchange = ccxt.bybit ({
    'apiKey': 'iltB7keoLpILeuIhkF',
    'secret': 'HCPAsZ3Cb5wVwlKK2HTkzyHlg0pn2cYdEaSV',
})
"""

class  bybitOrder(object):
    type = 'limit'
    side = 'sell'
    size = 0

    order_price = 0
    stop_loss = 0

    def __init__(self, monitor, sym, type='market', side='buy', amount=0, leverage=50):

        self.pos_MaxLossProc = 40     # max loss % per pos;  40%;

        self.pos = None
        self.sl_id = None
        self.sl_order = "None"
        
        self.monitor = monitor
        self.exc = monitor._exchange    # low level

        self.sym  = sym  + ":USDT" #BTC/USDT:USDT"
        self.type = type.lower()
        self.side = side.lower()

        self.coin_price = self.exc.fetch_ticker( self.sym )['last']

        self.check_leverage_and_size( leverage, amount )

        self.monitor.logInfo( " tradePos: Order==========================:" )
        self.monitor.logInfo( self.sym, self.type, self.side, f"size={self.size}")

    @classmethod
    def init(cls, monitor, msg: dict):
        """
        Create a bybitOrder instance from a message dictionary.
        :param msg: Dictionary containing order details.
        :return: bybitOrder instance.
        """
        monitor = monitor
        sym = msg.get('sym', 'BTC/USDT')
        type = msg.get('type', 'market')
        side = msg.get('side', 'buy')
        size = msg.get('size', 0)
        leverage = msg.get('leverage', 50)

        return cls(monitor, sym, type, side, size, leverage)

    def check_leverage_and_size(self, leverage, amount ):
        self.set_leverage( leverage)

        self.usd = amount  # USDT
        self.check_position_size()

    def set_leverage(self, leverage=0):

        s1 = self.sym.split('/')  # 'MANA/USDT:USDT'
        s2 = s1[1].split(':')  # USDT:USDT
        sym = s1[0] + s2[1]  # 'MANAUSDT'

        rc = self.exc.fetch_leverage_tiers([sym], {'symbol': sym})
        lev = int(rc[self.sym][0]['maxLeverage'])

        if leverage > 0: self.leverage = leverage
        if lev < self.leverage: self.leverage = lev

        if lev != self.leverage:
            try:
                rcl = self.exc.set_leverage(self.leverage, self.sym)
            except Exception as e:
                self.monitor.logInfo("OpenPosition Exception: ", e)
                self.monitor.logException(e)
                # if 'retcode' == 110043 - leverage is not modify

        self.monitor.logInfo( f"tradePos: Leverage = {self.leverage} " )

    def check_position_size(self):

        # leverage = 1; price = 100 X/USDT; money = $100 USD; pos = 100 USDT ( 1 X/USDT )
        # price2 = 90 X/USDT; price change = -$10 = -10%  pos change = -$10; money loss = -$10 = 10%

        # leverage = 10; price = 100 X/USDT; money = $100 USD; pos = 1000 USDT   ( 10 * X/USDT )
        # price2 = 90 X/USDT; price change = -$10 = -10%  pos change = 10 * price change = -$100; money loss = 100%

        # price change = D%  pos change = ( D% * leverage )% = L%  money loss = L%

        self.size = self.usd * self.leverage / self.coin_price  # number of coins

        PriceChangeProc = ( self.pos_MaxLossProc/self.leverage ) / 100
        self.stop_loss = self.coin_price * (1 + ( -PriceChangeProc if self.side == 'buy' else PriceChangeProc ) )

#    def openPosition(self, tp=[0,0,0], tpd=[0,0,0], tpsize=[0,0,0], order_price=0, sl=[0,0] ):
    def openPositionX(self, tp=[0,0,0], tpsize=[0,0,0], sl=[0,0] ):
        #self.entry_price = order_price
        #self.order_price = order_price
        self.tp = tp
        self.tpsize = tpsize

        cur_price = order_price
        if self.type == 'market':
            tik = self.exc._exchange.fetch_ticker(self.sym)
            #self.order_price = int(tik['info']['markPrice'])
            cur_price = tik['last']

        if sl[0] > 0: self.stop_loss = sl[0]
        else:
            self.stop_loss  = cur_price - sl[1] if self.side == 'buy' else cur_price + sl[1]

        for i in range(3):
            if self.tp[i] == 0:
                self.tp[i] = cur_price + tpd[i] if self.side == 'buy' else cur_price - tpd[i]

        p = {
            'tpslMode': 'Partial',
            'tpSize': str( tpsize[2] ),
            'slSize': str(self.size),

            'takeProfit': {
                'triggerPrice': self.tp[2],
                'price': self.tp[2],
                'amount': 0.0,
                'type': 'limit',
                'priceType': 'mark'  # last, index
            },
            'stopLoss': {
                'triggerPrice': self.stop_loss,
                'price': self.stop_loss,
                'amount': 0.0,
                'type': 'limit',
                'priceType': 'mark'  # last, index
            }
        }
        ord = self.exc.create_order_with_take_profit_and_stop_loss(
              self.sym, self.type, self.side, self.size, params=p )

        self.sl_id = ord['id']

        self.pos = self.monitor.FetchOpenPosition(self.sym)
        self.entry_price = self.pos['entryPrice']

        if self.entry_price is not None:
            self.changeSL( self.stop_loss )
            return True

        self.addTPLimit( self.tpsize[0], self.tp[0] )
        self.addTPLimit( self.tpsize[1], self.tp[1] )

        return False

    def openPosition(self, tp=[], sl=[0,0] ):

        len_tp = len( tp )
        if len_tp == 0 or len_tp > 4 :
            self.monitor.logError("tradePos **************   size of TP is incorrect ")
            return None

        self.tp = tp
        self.sl = sl

        if self.sl[0] == 0:
            self.sl[0] = self.stop_loss

        # check tp sizes
        if   len_tp == 1:
            self.tpsize = [ self.size ]

        elif len_tp == 2:
            self.tpsize = [self.size * 0.5, self.size * 0.5 ]

        elif len_tp == 3:
            self.tpsize = [self.size * 0.4, self.size * 0.4, self.size * 0.2 ]

        elif len_tp == 4:
            self.tpsize = [self.size * 0.3, self.size * 0.3, self.size * 0.2, self.size * 0.2 ]

        n = len_tp - 1
        p = {
            'tpslMode': 'Partial',
            'tpSize': str( self.tpsize[n] ),
            'slSize': str(self.size),

            'takeProfit': {
                'triggerPrice': tp[n],
                'price': tp[n],
                'amount': self.tpsize[n],
                'type': 'limit',
                'priceType': 'mark'  # last, index
            },
            'stopLoss': {
                'triggerPrice': sl[0],
                'price': sl[0],
                'amount': self.size,
                'type': 'limit',
                'priceType': 'mark'  # last, index
            }
        }

        try:
            self.monitor.logInfo( "tradePos Order parameters ==========================:" )
            self.monitor.logInfo( p )

            self.monitor.logInfo( " ===============:")
            self.monitor.logInfo( "tradePos: Create Main Order ===============:")

            #ord = self.exc.create_order_with_take_profit_and_stop_loss(
            ord = self.exc.create_order(
                  self.sym, self.type, self.side, self.size, params=p )

            self.monitor.logInfo( " ===============:")
            self.monitor.logInfo( "tradePos: Fetch position ===============:")

            self.pos = self.exc.fetch_position(self.sym, {})

            self.entry_price = self.pos['entryPrice']
            self.monitor.logInfo(f"tradePos: Order Entry price: {self.entry_price}")

            self.monitor.logInfo( "tradePos: Create TP/SL ===============:")

            for i in range( len_tp ):
                if self.tp[i] > 0 and self.tpsize[0] > 0:
                    self.monitor.logInfo(f"tradePos: Create TP/SL ===============: {i}")
                    self.addTPLimit( self.tpsize[i], self.tp[i] )

            self.monitor.logInfo( " ===============:")
            self.monitor.logInfo( "tradePos: Fetch orders ===============:")

            self.orders = self.exc.fetch_open_orders(self.sym )

            for ord in self.orders:
                if 'StopLoss' in ord['info']['createType']:
                    self.sl_order = ord

        except Exception as e:
            self.monitor.logInfo("OpenPosition Exception: ", e )
            self.monitor.logException(e)

        return self.pos

    def readPosition(self):
        self.pos = self.exc.FetchOpenPosition(self.sym)
        self.entry_price = self.pos['entryPrice']
        if self.entry_price is not None:
            #self.type = self.pos['type']
            self.side = self.pos['info']['side'].lower()
            self.size = float(self.pos['info']['size'])
            self.order_price = self.entry_price

            return True
        return False

    def waitOpenPosition(self, timeout=1):
        while timeout > 0:
            self.pos = self.exc.FetchOpenPosition( self.sym )
            self.entry_price = self.pos['entryPrice']
            if self.entry_price is not None:
                return True
            time.sleep(1)
            timeout -= 1

        return False

    def addTPLimit(self, size, price ):
        side = 'sell' if self.side == 'buy' else 'buy'
        p = {'tpSize': str(size), 'tpslMode': 'Partial', 'PositionTpSl': True}

        return self.exc.create_take_profit_order( self.sym, 'limit', side, size, price, takeProfitPrice=price, params=p )


    def addTP__(self, size, d_price, d_tr_price = 1):
        if self.side == 'buy':
            side = 'sell'
            tp_price = self.order_price + d_price
            tr_price = tp_price - d_tr_price
        else:
            side = 'buy'
            tp_price = self.order_price - d_price
            tr_price = tp_price + d_tr_price

        param = {
            'takeProfitPrice': tr_price,
            'tpSize': str(size),
            'positionIdx': 0,
            'PositionTpSl': True
        }
        self.exc.CreateTakeProfitandStopLoss2( self.sym, 'limit', side, size, tp_price, param=param )

    def EditLimitOrder(self, id, amount, price, tr_price ):
        side = 'sell' if self.side == 'buy' else 'buy'
        return self.exc._exchange.edit_order( id, self.sym, 'limit', side, amount, price, params={'triggerPrice': tr_price })

    def editSL(self, price, amount = None ):
        #dd = 'sell' if self.side == 'buy' else 'buy'
        amount = self.size if amount is None else amount
        return self.EditLimitOrder( self.sl_order['id'], amount, price, price )

    def str(self):
        if self.pos is not None:
            return ( "\n ================================="
                f" {self.sym} {self.type} {self.side} size={self.size} leverage= {self.leverage}\n"
                f" entry_price={self.entry_price} order_price={self.order_price}\n"
                f" takeProfit: {self.tp}  profitSize: {self.tpsize }\n"
                f" stopLoss: {self.sl}\n"
                f" SLOrder: {self.sl_order}\n"
                "=================================\n"
            )
        else:
            return "\n ********* Position is empty !  ************\n"

class  trade( object ):
    type = 'limit'
    side = 'sell'
    size = 0

    order_price = 0
    stop_loss = 0

    def __init__(self, exchange, sym, type=None, side=None, size=None):
        self.pos = {}
        self.sl_id = None

        self.exc = exchange
        self.sym  = sym
        self.type = type
        self.side = side
        self.size = size

    def openPosition(self, order_price=0, d_stop_loss=0 ):
        self.entry_price = order_price
        self.order_price = order_price
        self.stop_loss = d_stop_loss

        if self.type == 'market':
            tik = self.exc._exchange.fetch_ticker(self.sym)
            #self.order_price = int(tik['info']['markPrice'])
            self.order_price = tik['last']

        self.stop_loss  = self.order_price - d_stop_loss if self.side == 'buy' else self.order_price + d_stop_loss

        ord = self.exc._exchange.create_order_with_take_profit_and_stop_loss(self.sym, self.type, self.side, self.size,
                                                     self.order_price, None, self.stop_loss, {'tpslMode': 'partial'})

        self.sl_id = ord['id']

        self.pos = self.exc.FetchOpenPosition(self.sym)
        self.entry_price = self.pos['entryPrice']
        if self.entry_price is not None:

            self.changeSL( d_stop_loss )

            return True
        return False

    def readPosition(self):
        self.pos = self.exc.FetchOpenPosition(self.sym)
        self.entry_price = self.pos['entryPrice']
        if self.entry_price is not None:
            #self.type = self.pos['type']
            self.side = self.pos['info']['side'].lower()
            self.size = float(self.pos['info']['size'])
            self.order_price = self.entry_price

            return True
        return False

    def waitOpenPosition(self, timeout=1):
        while timeout > 0:
            self.pos = self.exc.FetchOpenPosition( self.sym )
            self.entry_price = self.pos['entryPrice']
            if self.entry_price is not None:
                return True
            time.sleep(1)
            timeout -= 1

        return False

    def addTP(self, size, d_price, d_tr_price = 1):
        if self.side == 'buy':
            side = 'sell'
            tp_price = self.order_price + d_price
            tr_price = tp_price - d_tr_price
        else:
            side = 'buy'
            tp_price = self.order_price - d_price
            tr_price = tp_price + d_tr_price

        param = {
            'takeProfitPrice': tr_price,
            'tpSize': str(size),
            'positionIdx': 0,
            'PositionTpSl': True
        }
        self.exc.CreateTakeProfitandStopLoss2( self.sym, 'limit', side, size, tp_price, param=param )


    def changeSL(self, d_price ):

        orders = self.exc.FetchOpenOrders( self.sym )
        for ord in orders:
            if ord['stopLossPrice'] is not None:
                self.stop_loss = self.entry_price + d_price if ord['side'].lower() == 'buy' else self.entry_price - d_price
                self.exc.EditOrder2( ord['id'], self.sym, ord['type'], ord['side'], ord['amount'], param={'stopLossPrice': self.stop_loss })
                return True
        """            
            self.stop_loss  = self.order_price - d_stop_loss if self.side == 'buy' else self.order_price + d_stop_loss
            # side for stopLoss order is invers to open order
            side = 'buy' if self.side == 'sell' else 'sell'
            self.exc.EditOrder2( self.sl_id, self.sym, 'market', side, self.size, param={'stopLossPrice': self.stop_loss} )
        """
        return False


    def print(self):
        print( f" Open:  {self.type}  {self.side}  {self.size} ")
        print( f" Open:  {self.order_price}  {self.entry_price}  stopLoss: {self.size}  {self.stop_loss}")