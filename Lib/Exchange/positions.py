# -*- coding: utf-8 -*-
from pprint import pprint

from ccxt.base.types import (Balances, Currency, Greeks,
     Int, Leverage, Market, MarketInterface, Num,
     Option, OptionChain,
     Order, OrderBook, OrderRequest, OrderSide, OrderType, Str,
    Strings, Ticker, Tickers, Trade, Transaction, TransferEntry)


from base_exchange import base_Exchange, Position, base_Order

from dataclasses import dataclass, field
from typing import Literal, Union, TypedDict, Optional, Any

from enum import Enum

class orderType(Enum):
    Market = "market"
    Limit = "limit"
    StopMarket = "StopMarket"
    StopLimit = "StopLimit"
    Info = "info"

class orderState(Enum):
    NotDef = 'not defined'
    Created = "created"
    Pending = "pending"
    Active  = "active"
    Closed  = "closed"
    Canceled= "canceled"

class orderSide(Enum):
    Buy = "buy"
    Sell= "sell"    

@dataclass
class orderData():
    id:    Optional[ str] = ''
    side:  Optional[ orderSide ] = None
    type:  Optional[ orderType ] = None
    usdt:  Optional[float] = 0
    coins: Optional[float] = 0 
    price: Optional[float] = 0 
    triggerPrice: Optional[float] = 0
    order:  Optional[base_Order] = None
    state:  Optional[orderState] = orderState.NotDef
    params: Optional[dict] = None

    def set(self, data: dict):
        for k, v in data.items():
            if k in self.__dict__:
                self.__dict__[k] = v


@dataclass
class BybitPosition:

    exc: Any
    symbol:   str     # 'BTC/USDT'
    leverage: float

    params: Optional[dict] = field(default_factory=dict)
    msg_timestamp: Optional[int] = None
    info: Optional[dict] = None
    # ---------------------------------

    main_order: Optional[orderData] = field(default_factory=orderData)
    sl_order: Optional[orderData]  = field(default_factory=orderData)
    tp1_order: Optional[orderData]  = field(default_factory=orderData)
    tp2_order: Optional[orderData]  = field(default_factory=orderData)
    tp3_order: Optional[orderData]  = field(default_factory=orderData)


    """
    entryPrice: float
    markPrice: float
    liquidationPrice: float
    initialMargin: float
    initialMarginPercentage: float
    maintenanceMargin: float
    maintenanceMarginPercentage: float
    unrealizedPnl: float
    percentage: Optional[float] = None
    contracts: Optional[float] = None
    notional: Optional[float] = None
    marginRatio: Optional[float] = None
    datetime: Optional[str] = None
    """
    
    def __post_init__( self ):
        s1 = self.symbol.split('/')  # 'MANA/USDT'
        self.symbol_s = s1[0] + s1[1]  # 'MANAUSDT'
        self.symbol_f = self.symbol +":"+s1[1]  # 'MANA/USDT:USDT'

        self._exc = self.exc._exchange
        self.set_leverage()
        orders = []

        positionSide: Literal['Long', 'Short']


    def set_leverage(self, leverage=0):

        #s1 = self.sym.split('/')  # 'MANA/USDT:USDT'
        #s2 = s1[1].split(':')  # USDT:USDT
        #sym = s1[0] + s2[1]  # 'MANAUSDT'

        rc = self._exc.fetch_leverage_tiers([self.symbol_s], {'symbol': self.symbol_s})
        lev = int( rc[ self.symbol_f ] [0]['maxLeverage'])

        if leverage > 0: self.leverage = leverage
        if lev < self.leverage: self.leverage = lev

        if lev != self.leverage:
            try:
                rcl = self._exc.set_leverage(self.leverage, self.symbol_f)
            except Exception as e:
                self.exc.logInfo("OpenPosition Exception: ", e)
                self.exc.logException(e)
                # if 'retcode' == 110043 - leverage is not modify

        self.exc.logInfo(f"tradePos: Leverage = {self.leverage} ")

    def set_Main_order(self, type: orderType, side: orderSide,
                         usdt=0, coins=0,
                         price=None, triggerPrice=None, parms=None):

        self.main_order.type = type
        self.main_order.side = side

        self.main_order.usdt = usdt
        self.main_order.coins = coins if coins > 0 else self.coinAmount( self.main_order.usdt ) # number of coins

        self.main_order.price = price
        self.main_order.triggerPrice = triggerPrice
        self.main_order.params = parms

        self.main_order.state = orderState.Created

    def add_StopLoss_order(self, type, usdt=0, coins=0, sl_price=0, sl_limit_price=None ):

        side = orderSide.Sell if self.main_order.side == orderSide.Buy else orderSide.Buy

        self.sl_order.side = side
        self.sl_order.type = type
        self.sl_order.usdt = usdt
        self.sl_order.coins = coins if coins > 0 else self.coinAmount( self.sl_order.usdt ) # number of coins
        self.sl_order.price = sl_limit_price
        self.sl_order.triggerPrice = sl_price

        self.params['stopLoss'] = {
            'amount': self.sl_order.coins,
            'price': sl_limit_price,
            'triggerPrice': sl_price,
            'type': type,  # 'market' or 'limit'
            'priceType': 'mark'  # last | mark | index
        }

        self.sl_order.state = orderState.Created
        pprint(self.params)

    def add_TakeProfit_order(self, num, type, usdt=0, coins=0, tp_price=0, tp_limit_price=None ):
        match num:
            case 1:
                ord = self.tp1_order
            case 2:
                ord = self.tp2_order
            case 3:
                ord = self.tp3_order
            case _:
                self.exc.logError(f"Position: add_takeProfit_order: unknown tp_num {num}")
                raise

        side = orderSide.Sell if self.main_order.side == orderSide.Buy else orderSide.Buy

        ord.side = side
        ord.type = type
        ord.usdt = usdt
        ord.coins = coins if coins > 0 else self.coinAmount( ord.usdt ) # number of coins
        ord.price = tp_limit_price
        ord.triggerPrice = tp_price

        self.params['takeProfit'] = {
            'amount': ord.coins,
            'price': tp_limit_price,
            'triggerPrice': tp_price,
            'type': type,           # 'market' or 'limit'
            'priceType': 'mark'  # last | mark | index
        }

    def open_TakeProfit_Part(self, type='market', usdt=0, coins=0, price=None, tp_price=0, params={}):
        # add a new takeProfit order
        # we have to have open position !
        side = orderSide.Sell if self.main_order.side == orderSide.Buy else orderSide.Buy

        coin = coins if coins > 0 else self.coinAmount( usdt ) # number of coins

        p = {
            'tpSize': str(coin),
            'tpslMode': 'Partial',
            'PositionTpSl': True
        }
        self.info = self._exc.create_take_profit_order( self.symbol_f, type,
                                            side.value, coin, price, tp_price, p )
        return self.info

    def open_StopLoss(self, type=orderType.Market, usdt=0, coins=0, price=None, sl_price=0, params={}):
        # add a new takeProfit order
        # we have to have open position !
        side = orderSide.Sell if self.main_order.side == orderSide.Buy else orderSide.Buy

        coin = coins if coins > 0 else self.coinAmount( usdt ) # number of coins

        self.info = self._exc.create_stop_loss_order(
            self.symbol_f, type.value, side.value, coin, price, sl_price, params )
        return self.info



    def x_create_mainOrder(self, side: orderSide,
                            type: orderType, 
                            usdt=0, coins=0, price=0, stopPrice=0):
        
        self.main_order.set( {
            'order': None,
            'state': orderState.Created,
            'side': side,
            'type': type
        })
                        #'usdt': usdt,
                        #'coins': coins,

                        #'price': price,
                        #'stopPrice': stopPrice }
        
        match type:
            case orderType.Market:
                self.main_order.price = None
                self.main_order.triggerPrice = None
                
            case orderType.Limit:
                if price == 0:
                    self.exc.logError(f"Position: add_openOrder: limit order need price {self.sym}")
                    return
                
                self.main_order.price = price
                self.main_order.triggerPrice = None

            case orderType.Stop:    
                if stopPrice == 0:
                    self.exc.logError(f"Position: add_openOrder: stop order need stopPrice {self.sym}")
                    return
            case _:
                self.exc.logError(f"Position: add_openOrder: unknown order type {type} {self.sym}")
                return
        self.monitor.logInfo(f"Position: add_openOrder: {self.open} {self.sym}")
        self.check_coinAmount()

    def _send_order(self):
        ord = self.main_order

        print( f"--> _send_order: {self.symbol}, {ord.type}, {ord.side}, {ord.coins=}, {ord.price=}, \n {ord.params=}" )

        if ord.type in  [ orderType.StopMarket, orderType.StopLimit ]:
            params = {
                'triggerDirection': 'above' if ord.side == orderSide.Buy else 'below'
            }
        #self.params = {'triggerDirection': 'up' if self.side == 'sell' else 'down'}

#            if stopPrice is None: stopPrice = self.stopPrice
            self.info = self._exc.create_stop_order( self.symbol_f, ord.type.value, ord.side.value,
                    ord.coins, ord.price, ord.triggerPrice, params=self.params)
        else:
#            self.last_order = self._exc.create_order( self.symbol_f, ord.type.value,
#               ord.side.value, ord.coins, ord.price, self.params )

            self.last_order = {'id':456}  # fake id
            print( " Open Order:")
            print( f" {self.symbol_f=} {ord.type.value=}\
            {ord.side.value=} {ord.coins=} {ord.price=} {self.params=}" )

        print( f'Sent order {self.last_order['id'] = }' )

        return self.last_order


        if self.open['state'] != orderState.Created:
            self.exc.logError(f"Position: _send_order: position already opened {self.sym}")
            return

        self.open['state'] = orderState.Pending
        self.monitor.logInfo(f"Position: _send_order: {self.open} {self.sym}")

        self.open['order'].openMaker_Market()
        self.orders.append( self.open['order'] )

        self.open['state'] = orderState.Active

    def open(self):

        if self.main_order.state != orderState.Created:
            self.exc.logError(f"Position: openOrder: position has wrong state {self.main_order.state } {self.symbol}")
            return

        return self._send_order()
    


        self.open['state'] = orderState.Pending
        self.monitor.logInfo(f"Position: openOrder: {self.open} {self.sym}")

        self.open['order'].openMaker_Market()
        self.orders.append( self.open['order'] )

        self.open['state'] = orderState.Active



    def run(self, action):
        actions = action.split('|')
        
        if 'open' in actions and self.open['state'] != 'created':
            self.exc.logError(f"Position: run: position already opened {self.sym}")
            return
        
        for act in actions:
            if act == 'open':
                self.open['order']= BybitOrder.CreateMarketOrder(self.exc, self.symbol,
                                                                 self.open['side'],
                                                                self.open['coins'],
                                                                self.open['usdt'],
                                                                self.leverage   )
                
            elif act == 'stoploss':
                self.stopLoss()
                self.open['order'].add_StopLossData(    )

            elif act == 'takeprofit1':
                self.takeProfit1()
                self.open['order'].add_TakeProfitData(   )

            elif act == 'takeprofit2':
                self.takeProfit2()

            elif act == 'takeprofit3':
                self.takeProfit3()
            else:
                self.monitor.logError(f"Position: run: unknown action {act}")

        self.open['order'].openMaker_Market()



    def modify(self, order_type, sl_price=0, usdt=0):
        if order_type == 'stoploss':
            self.stopLoss = {'sl_price': sl_price, 'usdt': usdt}    
        elif order_type == 'takeprofit1':
            self.takeProfit1 = {'tp_price': sl_price, 'usdt': usdt}
        elif order_type == 'takeprofit2':
            self.takeProfit2 = {'tp_price': sl_price, 'usdt': usdt}
        elif order_type == 'takeprofit3':
            self.takeProfit3 = {'tp_price': sl_price, 'usdt': usdt} 
        else:
            self.monitor.logError(f"Position: modify: unknown order_type {order_type}")

    def cancel(self, action):
        actions = action.split('|')
        for act in actions:
            if act == 'stoploss':
                self.stopLoss = None    
            elif act == 'takeprofit1':
                self.takeProfit1 = None
            elif act == 'takeprofit2':
                self.takeProfit2 = None
            elif act == 'takeprofit3':
                self.takeProfit3 = None 
            else:
                self.monitor.logError(f"Position: cancel: unknown action {act}")
    
    def close(self):
        self.monitor.logInfo(f"Position: close position {self.sym}")
        # close all orders and position on exchange

    def coinPrice(self):
        """
        Get the current price of the coin.
        :return: Current coin price.
        """
        return self.exc.get_ticker_price( self.symbol )

    def coinAmount(self, usdt ):
        return usdt * self.leverage / self.coinPrice()  # number of coins

