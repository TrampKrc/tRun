# -*- coding: utf-8 -*-
import os
import sys
#from sortedcontainers import SortedDict

from Tools import tools

import logging
from pprint import pprint
from base_exchange import base_Exchange, Position, Order

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt.pro  # noqa: E402

"""binanceDemo:
ApiKey = 2859697235c76211b67f9385b98569918b54ae3bc6f44d338a3ff4dabb6ac741
Secret = 0806f17840928dd3a6b0bce7a411bd399bc3390297962866a1430bf126da3ba6

Work:
UZDSvsFXNfPZl5TcPJT8FnUHrQOo0LuhGKbhouJyE0MTNhbOYsbkT5bwn6jq8ftf
plvD0YldyWYF1uYekJuMrgBu9ki1Vd8btojVAeqBHIis7xhPy8WEzgiRxx5RzJ8u

"""

class jBinance( base_Exchange ):

    def __init__(self, name, key: str, secret: str, demo=None ):

        super().__init__( name, key, secret)
        self._cl_name = self.__class__.__name__

        self._create( demo )

        #self._test_print_position()
        #self._test_print_order()
        

        #exchange = getattr(ccxt.pro, 'binance')()
        # config = { 'apiKey': 'YOUR_API_KEY',  'secret': 'YOUR_SECRET'}
        #for attr, value in config.items():
          #setattr(exchange, attr, value)

    def ex(self):
      return self._exchange


    def _create( self, demo=None ):

        self._exchange = ccxt.pro.binance( {'apiKey': self._apiKey, 'secret': self._apiSecret, 'enableRateLimit': True,
                                        'options': {'defaultType': 'future'} })
        if demo:
            self._demo = True
            self._exchange.set_sandbox_mode( True )

        #markets = exchange.load_markets() # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        #self._exchange.verbose = True  # uncomment for debugging


    async def Order_CancelAll(self, symbol=None, params={}):
        return  await self._exchange.cancel_all_orders( symbol, params)

    async def Order_Cancel( self, id, symbol=None, params={} ):
        return await self._exchange.cancel_order( id, symbol, params)

    async def Order_Limit(self, symbol, side, amount, price, params={}):
        return await self._exchange.create_order(symbol, 'limit', side, amount, price, params)

    async def Order_Market(self, symbol, side, amount, price=None, params={}):
        return await self._exchange.create_order(symbol, 'market', side, amount, price, params)

    async def Order_Limit_Buy(self, symbol, amount, price, params={}):
        return await self._exchange.create_order(symbol, 'limit', 'buy', amount, price, params)

    async def Order_Limit_Sell(self, symbol, amount, price, params={}):
        return await self._exchange.create_order(symbol, 'limit', 'sell', amount, price, params)

    async def Order_Market_Buy(self, symbol, amount, params={}):
        return await self._exchange.create_order(symbol, 'market', 'buy', amount, None, params)

    async def Order_Market_Sell(self, symbol, amount, params={}):
        return await self._exchange.create_order(symbol, 'market', 'sell', amount, None, params)



    async def Order_Post_Only(self, symbol, type, side, amount, price, params={}):
        return await self._exchange.create_post_only_order(symbol, type, side, amount, price, params)

    async def Order_Reduce_Only(self, symbol, type, side, amount, price, params={}):
      return await self._exchange.create_reduce_only_order(symbol, type, side, amount, price, params)

    async def Order_Stop(self, symbol, type, side, amount, price=None, stopPrice=None, params={}):
      return await self._exchange.create_stop_order( symbol, type, side, amount, price, stopPrice, params)

    async def Order_Stop_Limit(self, symbol, side, amount, price, stopPrice, params={}):
      return await self._exchange.create_stop_limit_order( symbol, side, amount, price, stopPrice, params)

    async def Order_Stop_Market(self, symbol, side, amount, stopPrice, params={}):
      return await self._exchange.create_stop_market_order( symbol, side, amount, stopPrice, params )



    async def Get_Active_Data(self, p='futures'):
        return await self._exchange.fetch_balance({'type':p})


    def Get_Balance( self, data ):
        print(tools.yellow('-------------------------- balance ------'))
        
        tmp = []
        coin = 0
        print( data['total'])
        for coin, val in data['total'].items():
          if val != 0:
            tmp.append( coin )
            print( coin )
        
        for ct in tmp:
          print( 'tmp', ct )
          for cc in data['info']['assets']:
            #print( 'cc ', cc )
            if cc['asset'] == ct:
               self._activeBalances[ coin ] = cc
               print( cc )
               logging.info( cc )
               break


        print( "-----------------  Balance  ----------------------")
        for cc, bal in self._activeBalances.items():
          print( cc, bal )
        print(tools.pink('-------------------------- balance end ------'))

        return self._activeBalances


    def get_derivatives_balance(self, params={}):
  
      balances = self._exchange.fetch_derivatives_balance(params)
  
      for balance in balances['result']['list']:
        print(balance)
  
      print(balances)


    def Get_Open_Positions( self, tdict=None ):

        tools.dump(tools.green(self._exchange.id), 'parsing positions...')
        positions = tdict #if tdict else self._exchange.fetch_balance({'type':'future'})
        print( positions['info']['positions'] )
        
        self._activePositions = SortedDict( self._collect_positions( positions['info']['positions'] ) )
        return self._activePositions


    def check_position(self, symbol ):
        linear_positions = self._exchange.fetch_positions()  # [ symbol ], params)
        pprint(linear_positions)
    
        print(" ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; ")
        pprint(self._exchange.parse_positions(linear_positions))

    def Get_Position(self, test_symbol=None ):
        symbol = 'BTC/USDT:USDT' if test_symbol is None else test_symbol  # https://docs.ccxt.com/en/latest/manual.html#contract-naming-conventions
        market = self._exchange.market(symbol)
        params = {'subType': 'linear' if market['linear'] else 'inverse'}
        linear_positions = self._exchange.fetchPositions ( [symbol], params = {})

        # -----------------------------------------------------------------------------
    
        symbol = 'BTC/USD:BTC'
        market = self._exchange.market(symbol)
        params = {'subType': 'linear' if market['linear'] else 'inverse'}
    
        inverse_positions = self._exchange.fetch_positions([ symbol ], params)
        pprint(inverse_positions)


    def _parse_orders( self, orders ):

      for order in orders:
        new_order = Binance_Order(order)
        self._activeOrders[order['id']] = new_order
        print(tools.green('\nOrder:'), order)
        # logging.info( " Open Order")
        # logging.info( order )
    
        if new_order.is_NewPosition(self._activePositions):
          # execute
          pass

      # orders = self.exchange.fetch_derivatives_orders( symbol, since, limit, params)
      # orders2 = self.exchange.fetch_derivatives_orders( symbol, since, limit, params)

      # trades = self.exchange.fetch_derivatives_trades( symbol, since=None, limit=None, params={}):
      # trades = self.exchange.fetch_derivatives_trades( symbol, since, limit, params )
  
      return self._activeOrders

    async def Get_Open_Orders(self, symbol=None, since=None, limit=None, params={}):
  
      self._exchange.options["warnOnFetchOpenOrdersWithoutSymbol"] = False
      orders = await self._exchange.fetch_open_orders(symbol, since, 300, params)
  
      #return self._parse_orders(orders)
      return self._parse_orders(orders)

    async def get_derivatives_open_orders( self, symbol=None, since=None, limit=None, params={}):
# ccxt.base.errors.ExchangeError: binance fetchOpenOrders() WARNING: fetching open orders without specifying a symbol is rate-limited to one call per 144 seconds.
# Do not call self method frequently to avoid ban. Set binance.options["warnOnFetchOpenOrdersWithoutSymbol"] = False to suppress self warning message.
 
      self._exchange.options["warnOnFetchOpenOrdersWithoutSymbol"] = False
      orders = await self._exchange.fetch_open_orders(symbol, since, 300, params)

      return self._parse_orders(orders)


    def _test_print_position(self):
      pos = Position({
        "symbol": "THETAUSDT",
        "initialMargin": "11.28909417",
        "maintMargin": "2.25781883",
        "unrealizedProfit": "12.19097356",
        "positionInitialMargin": "11.28909417",
        "openOrderInitialMargin": "0",
        "leverage": "20",
        "isolated": False,
        "entryPrice": "1.0959",
        "maxNotional": "250000",
        "positionSide": "BOTH",
        "positionAmt": "194.9",
        "notional": "225.78188356",
        "isolatedWallet": "0",
        "updateTime": 1676464603767,
        "bidNotional": "0",
        "askNotional": "394.80225000"
      })
      
      dd = pos.leverage
      dd2 = pos['leverage']
      
      dd3 = pos['_coin']
      
      logging.info( self.position_heads() )
      logging.info( self.position_value(pos) )
      k = 0
      
    def _test_print_order( self ):
        order = Binance_Order(
          {'info':
             {'orderId': '15391537750',
              'symbol': 'ATOMUSDT',
              'status': 'NEW',
              'clientOrderId': 'x-v69H3rG167112285069d4b1d',
              'price': '22.310',
              'avgPrice': '0',
              'origQty': '2.88',
              'executedQty': '0',
              'cumQuote': '0',
              'timeInForce': 'GTC',
              'type': 'LIMIT',
              'reduceOnly': True,
              'closePosition': False,
              'side': 'SELL',
              'positionSide': 'BOTH',
              'stopPrice': '0',
              'workingType': 'CONTRACT_PRICE',
              'priceProtect': False,
              'origType': 'LIMIT',
              'time': '1676148649878',
              'updateTime': '1676148649878'
              },
           'id': '15391537750',
           'clientOrderId': 'x-v69H3rG167112285069d4b1d',
           'timestamp': 1676148649878,
           'datetime': '2023-02-11T20:50:49.878Z',
           'lastTradeTimestamp': None,
           'symbol': 'ATOM/USDT:USDT',
           'type': 'limit',
           'timeInForce': 'GTC',
           'postOnly': False,
           'reduceOnly': True,
           'side': 'sell',
           'price': 22.31,
           'triggerPrice': None,
           'amount': 2.88,
           'cost': 0.0,
           'average': None,
           'filled': 0.0,
           'remaining': 2.88,
           'status': 'open',
           'fee': {'currency': None, 'cost': None, 'rate': None},
           'trades': [],
           'fees': [{'currency': None, 'cost': None, 'rate': None}],
           'stopPrice': None
           }
        )
        
        logging.info( self.order_heads() )
        logging.info( self.order_value( order ) )


class Binance_Order(Order):
  """
{'info':
    { 'orderId': '15391537750',
      'symbol': 'ATOMUSDT',
      'status': 'NEW',
      'clientOrderId': 'x-v69H3rG167112285069d4b1d',
      'price': '22.310',
      'avgPrice': '0',
      'origQty': '2.88',
      'executedQty': '0',
      'cumQuote': '0',
      'timeInForce': 'GTC',
      'type': 'LIMIT',
      'reduceOnly': True,
      'closePosition': False,
      'side': 'SELL',
      'positionSide': 'BOTH',
      'stopPrice': '0',
      'workingType': 'CONTRACT_PRICE',
      'priceProtect': False,
      'origType': 'LIMIT',
      'time': '1676148649878',
      'updateTime': '1676148649878'
    },
    'id': '15391537750',
    'clientOrderId': 'x-v69H3rG167112285069d4b1d',
    'timestamp': 1676148649878,
    'datetime': '2023-02-11T20:50:49.878Z',
    'lastTradeTimestamp': None,
    'symbol': 'ATOM/USDT:USDT',
    'type': 'limit',
    'timeInForce': 'GTC',
    'postOnly': False,
    'reduceOnly': True,
    'side': 'sell',
    'price': 22.31,
    'triggerPrice': None,
    'amount': 2.88,
    'cost': 0.0,
    'average': None,
    'filled': 0.0,
    'remaining': 2.88,
    'status': 'open',
    'fee': {'currency': None, 'cost': None, 'rate': None},
    'trades': [],
    'fees': [{'currency': None, 'cost': None, 'rate': None}],
    'stopPrice': None
}
  """
  
  def __init__(self, order):
    if order:
      super().__init__(order)

      self.init_order()
  
  def init_order(self):

    print(self.info)
    print(self.info.symbol)
    
    self._coin = self.info.symbol
    self._size = self.info.origQty
    self._price = self.info.price
    self._status = self.info.status  # 'NEW'
    self._type = self.info.type
    self._closePosition = self.info.closePosition
    self._side = self.info.side  # buy/sell
    self._time = self.info.time
    self._updatetime = self.info.updateTime
    self._id = self.id