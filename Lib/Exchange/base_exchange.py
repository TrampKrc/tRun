# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
from time import localtime, strftime
#import logging
from abc import ABC, abstractmethod

import config as acfg
import tools as T


#from pprint import pprint
#root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(root + '/python')

import ccxt  # noqa: E402
"""

exchange = ccxt.binance ({
    'rateLimit': 10000,  # unified exchange property
    'headers': {
        'YOUR_CUSTOM_HTTP_HEADER': 'YOUR_CUSTOM_VALUE',
    },
    'options': {
        'adjustForTimeDifference': True,  # exchange-specific option
    }
})
exchange.options['adjustForTimeDifference'] = False
"""

class base_Exchange( T.CfgAPI ):

    _name  : str = ''
    _apiKey: str = ''
    _apiSecret: str = ''
    _cfg_data: T.CfgJson

    _activeBalances: dict = {}
    _activePositions: dict = {}
    _activeOrders: dict = {}

    _ex_cfg :   dict = {}

    def __init__(self, ex_name, cfg_data ):     # cfg_data -> CfgJson class
        super().__init__( cfg_data )

        self._name = ex_name

        f_name = acfg.secrets
        if os.path.exists( f_name ):
            cfg_sec = T.read_json( f_name )

            if ( cfg_k := cfg_sec.get(ex_name, None) ) is not None:
                self._apiKey = cfg_k.get("Key", "not found")
                self._apiSecret = cfg_k.get("Secret", "not found")
            else:
                raise ValueError(f"Nof found section: {ex_name} ")

        else:
            raise ValueError(f"Nof found cfg file: {f_name} ")

        self._exchange = None

        self.logInfo(f"CCXT Version: {ccxt.__version__}")

        self._cl_name = self.__class__.__name__

        self._pos_format =[ {'Head': 'Coin'.ljust(10),        'vFmt': '{:<10}',   'Val': '_coin'},
                            {'Head': 'Size'.ljust(10),        'vFmt': '{:<10}',   'Val': '_size'},
                            {'Head': 'Price'.ljust(10),       'vFmt': '{:<10.8}', 'Val': '_entryPrice'},
                            {'Head': 'Liquidation'.ljust(12), 'vFmt': '{:<12.8}', 'Val': '_liqPrice'},
                            {'Head': 'Margin %'.ljust(10),    'vFmt': '{:<10.8}', 'Val': '_marginRatio'},
                            {'Head': 'Margin'.ljust(10),      'vFmt': '{:<10.8}', 'Val': '_margin'},
                            {'Head': 'Value'.ljust(10),       'vFmt': '{:<10.8}', 'Val': '_value'},
                            {'Head': 'PNL'.ljust(10),         'vFmt': '{:<10.8}', 'Val': '_unPNL'},
                            {'Head': 'PNL %'.ljust(10),       'vFmt': '{:<10.8}', 'Val': '_unPNLproc'},
                            {'Head': 'realPNL'.ljust(10),     'vFmt': '{:<10.8}', 'Val': '_rlzPNL'},
                            {'Head': 'Leverage'.ljust(10),    'vFmt': '{:<10}',   'Val': '_leverage'},
                            {'Head': 'ROI'.ljust(10),         'vFmt': '{:<10}',   'Val': '_roi'}
                        ]

        self._order_format = [{'Head': 'Coin'.ljust(10), 'vFmt': '{:<10}', 'Val': '_coin'},
                              {'Head': 'Size'.ljust(8), 'vFmt': '{:<8}', 'Val': '_size'},
                              {'Head': 'Price'.ljust(10), 'vFmt': '{:<10.8}', 'Val': '_price'},
                              {'Head': 'Status'.ljust(8), 'vFmt': '{:<8}', 'Val': '_status'},
                              {'Head': 'Type'.ljust(12), 'vFmt': '{:<12}', 'Val': '_type'},
                              {'Head': 'ClosePos'.ljust(9), 'vFmt': '{:<8}', 'Val': '_closePosition'},
                              {'Head': 'Side'.ljust(5), 'vFmt': '{:<5}', 'Val': '_side'},
                              {'Head': 'Time'.ljust(15), 'vFmt': '{:<15}', 'Val': '_time'},
                              {'Head': 'UpdateTime'.ljust(15), 'vFmt': '{:<15}', 'Val': '_updatetime'}
                            ]

    def _str_heads(self, tdict ):
      return ''.join( [k['Head'] for k in tdict] )

    def _str_values(self, tdict, el):
      """
      try:
        for k in tdict:
          a = k['Val']
          b = el[ k['Val'] ]
          c =  k['vFmt'].format( el[ k['Val'] ])

      except Exception as e:
          print( 'k={} k[Val]={}, b={} '.format( k, a, b ) )
          g = 0
      """
      return ''.join( [ k['vFmt'].format( el[k['Val']]) for k in tdict ])

    def position_heads(self):
      return  self._str_heads( self._pos_format )

    def position_value(self, pos):
      return  self._str_values( self._pos_format, pos )
    
    def order_heads(self):
      return  self._str_heads( self._order_format )

    def order_value(self, order):
      return  self._str_values( self._order_format, order )

    def log_balance(self, balance = None):
      self.logInfo( "-----------------  Balance  ----------------------", False)
  
      data = balance if balance else self._activeBalances
      for cc, bal in data.items():
        self.printInfo( bal, False )

    def log_positions(self, positions=None):
      self.printInfo( " ------------------  Positions: {} ----------------".format(len(self._activePositions)))
      self.printInfo( self.position_heads() )
      
      data = positions if positions else self._activePositions
      for c, p in data.items():
        self.printInfo(self.position_value(p))

    def log_orders(self, orders):
      self.printInfo(" ------------------  Orders: {} : {} ----------------".format(self._name, len(self._activeOrders)))
      self.printInfo(self.order_heads())
      
      data = orders if orders else self._activeOrders
      for c, p in data.items():
        self.printInfo(self.order_value(p))

    def _collect_positions(self, positions ):
      new_pos = None
      for pos in positions:
        print( 'pp--->>>  ', pos )
        new_pos = Position(pos)
        print('pp2--->>>  ', new_pos)
        print('pp3--->>>  ', new_pos._size )
        if float(new_pos._size) != 0.:
          self._activePositions[ new_pos._coin ] = new_pos
          print('pp4---->', pos)
      #    logging.info( " Positions: ")
      #    logging.info( pos )

      return self._activePositions
    """
    def str_position(self, pos ):
        self._format = [{'Head': 'Coin'.ljust(10), 'vFmt': '{:<10}', 'Val': self._coin},
                        {'Head': 'Size'.ljust(10), 'vFmt': '{:<10}', 'Val': self._size},
                        {'Head': 'Price'.ljust(10), 'vFmt': '{:<10}', 'Val': self._entryPrice},
                        {'Head': 'Liquidation'.ljust(10), 'vFmt': '{:<10}', 'Val': self._liqPrice},
                        {'Head': 'Margin %'.ljust(10), 'vFmt': '{:<10}', 'Val': self._marginRatio},
                        {'Head': 'Margin'.ljust(10), 'vFmt': '{:<10}', 'Val': self._margin},
                        {'Head': 'Value'.ljust(10), 'vFmt': '{:<10}', 'Val': self._value},
                        {'Head': 'PNL'.ljust(10), 'vFmt': '{:<10}', 'Val': self._unPNL},
                        {'Head': 'PNL %'.ljust(10), 'vFmt': '{:<10}', 'Val': self._unPNLproc},
                        {'Head': 'realPNL'.ljust(10), 'vFmt': '{:<10}', 'Val': self._rlzPNL},
                        {'Head': 'ROI'.ljust(10), 'vFmt': '{:<10}', 'Val': self._roi}
                        ]

    
    def connect( self ):
    
        if self._name == 'Bybit':
          self._exchange = ccxt.bybit( {'apiKey': self._apiKey, 'secret': self._apiSecret } )
          
        elif self._name == 'Binance':
          self._exchange = ccxt.binance( {'apiKey': self._apiKey, 'secret': self._apiSecret} )
          self._exchange.set_sandbox_mode( True )

        #markets = exchange.load_markets() # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        #self._exchange.verbose = True  # uncomment for debugging


    def check_balance( self):
        # -----------------------------------------------------------------------------
        print('-------------------------- balance ------')
        balances = self._exchange.fetch_balance()
        #what !+ 0:
        
        for coin, val in balances['total'].items():
            if val != 0:
                print ( coin )
                break
            
        for cc in balances['info']['result']['list']:
            if cc['coin'] == coin:
                print( cc )
            
            
        #print(  balances )
        print('-------------------------- balance end ------')
      
      
    def check_derivatives_balance(self, params={}):
      
        balances = self._exchange.fetch_derivatives_balance( params )

        for balance in balances['result']['list']:
          print( balance )

        print ( balances )
      

    def check_positions( self):
        tools.dump( tools.green( self._exchange.id), 'fetching positions...')
        
        positions = self._exchange.fetch_positions()  # [ symbol ], params)
        
        for pos in positions:
          
            self._activePositions[ pos['info']['symbol'] ] = Position( pos )
            
            tools.dump( tools.green( pos['symbol'] ),
                        tools.green( pos['initialMargin']),
                        tools.green( pos['initialMarginPercentage']),
                        tools.green( pos['maintenanceMargin']),
                        tools.green( pos['entryPrice']),
                        tools.green( pos['notional']),
                        tools.green( pos['leverage']),
                        tools.green( pos['unrealizedPnl']),
                        tools.green( pos['contracts']),
                        tools.green( pos['marginRatio']),
                        tools.green( pos['liquidationPrice']),
                        tools.green( pos['markPrice']),
                        tools.green( pos['collateral']),
                        tools.green( pos['collateral']),
                        tools.green( pos['marginMode']),
                        tools.green( pos['side']),
                        tools.green( pos['percentage']),
                        tools.green( pos['info']['symbol']),
                        #tools.green( pos['info']['side']),
                        tools.green( pos['info']['size']),
                        tools.green( pos['info']['positionValue']),
                        tools.green( pos['info']['positionBalance']),
                        tools.green( pos['info']['liqPrice']),
                        tools.green( pos['info']['takeProfit']),
                        tools.green( pos['info']['stopLoss']),
                        tools.green( pos['info']['trailingStop']),
                        tools.green( pos['info']['createdTime']),
                        tools.green( pos['info']['updatedTime']),
                        tools.green( pos['info']['markPrice']),
                        tools.green( pos['info']['cumRealisedPnl']),
                        tools.green( pos['info']['positionMM']),
                        tools.green( pos['info']['positionIM']),
                        tools.green( pos['info']['occClosingFee'])
                        )
            
            print ( pos )
        
        #pprint(positions)
    
        print(" ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; ")
        #pprint(  self._exchange.parse_positions(positions) )   # no for binance

    def check_position(self, symbol ):
        linear_positions = self._exchange.fetch_positions()  # [ symbol ], params)
        pprint(linear_positions)
    
        print(" ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; ")
        pprint(self._exchange.parse_positions(linear_positions))

    def test_position(self, test_symbol=None ):
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


    def check_derivatives_open_orders( self, symbol=None, since=None, limit=None, params={}):

        #orders = self._exchange.fetch_derivatives_open_orders( symbol=None, since=None, limit=None, params={})
        #orders = self._exchange.fetch_derivatives_open_orders( symbol, since, limit, params)
        orderss = self._exchange.fetch_derivatives_orders( symbol, since, limit, params)


        for order in orders:
          new_order = Order( order )
          self._activeOrders[order['info']['symbol']] = new_order
          
          if new_order.is_NewPosition( self._activePositions):
            # execute
            pass
        
  

  
  
          
          
        #orders = self.exchange.fetch_derivatives_orders( symbol, since, limit, params)
        #orders2 = self.exchange.fetch_derivatives_orders( symbol, since, limit, params)

        #trades = self.exchange.fetch_derivatives_trades( symbol, since=None, limit=None, params={}):
        #trades = self.exchange.fetch_derivatives_trades( symbol, since, limit, params )

        kk = 9

    """


class Position( T.mash ):
  """
{
"symbol":"THETAUSDT",
"initialMargin":"11.28909417",
"maintMargin":"2.25781883",
"unrealizedProfit":"12.19097356",
"positionInitialMargin":"11.28909417",
"openOrderInitialMargin":"0",
"leverage":"20",
"isolated":false,
"entryPrice":"1.0959",
"maxNotional":"250000",
"positionSide":"BOTH",
"positionAmt":"194.9",
"notional":"225.78188356",
"isolatedWallet":"0",
"updateTime":1676464603767,
"bidNotional":"0",
"askNotional":"394.80225000"
}
{"symbol":"HBARUSDT","initialMargin":"27.89923900","maintMargin":"3.74384780",
"unrealizedProfit":"-114.88328830",
"positionInitialMargin":"18.71923900",
"openOrderInitialMargin":"9.18000000",
"leverage":"20","isolated":false,
"entryPrice":"0.0835213588256","maxNotional":"25000","positionSide":"BOTH","positionAmt":"5858","notional":"374.38478000","isolatedWallet":"0","updateTime":1677079056193,"bidNotional":"183.60000000","askNotional":"914.48312000"}
  """
  
  def __init__(self, position):
    if position:
      super().__init__(position)
      
      self._info = position
      
      self._coin = position['symbol']
      self._size = position['positionAmt']
      self._entryPrice = position['entryPrice']
      self._liqPrice = 7.  # position['']  # liquidation Price
      self._marginRatio = 7.  # position['']
      self._margin = position['initialMargin']  # usdt from my acc
      self._value = position['notional']  # usdt in position =  margin when open * leverage
      self._unPNL = position['unrealizedProfit']
      self._unPNLproc = 7.  # position['']
      self._rlzPNL = 7.  # position['']
      self._leverage = position['leverage']
      self._updateTime = position['updateTime']
      self._roi = 7.  # position['']
      

class base_Order( ABC ):
  side_Buy = 'Buy'
  side_Sell = 'Sell'
  
  type_Limit = 'Limit'
  type_Market = 'Market'
  type_Stop_Loss = 'STOP_LOSS'
  type_Stop_Loss_Limit = 'STOP_LOSS_LIMIT'
  type_Take_Profit = 'TAKE_PROFIT'
  type_Take_Profit_Limit = 'TAKE_PROFIT_LIMIT'
  type_Limit_Maker = 'LIMIT_MAKER'
  
  action_Maker = 'MAKER'
  action_Taker = 'TAKER'
  
  resource_name = 'orders'
  test: bool = False

  @abstractmethod
  def get_order_type(self):
      pass

  def __init__(self,
               monitor, sym="", type="market", side='buy', coin_amount=0, usd=0, leverage=1,
               price=None, stopPrice=None, takeProfit = None, stopLoss=None, id='' ):

      self.monitor = monitor        # Exchange wrapper class: cfg + logger + wrapper methods
      self.exc = monitor._exchange  # exchange low level

      self.sym = sym  # BTC/USDT"
      self.symbol = sym + ":USDT"  # BTC/USDT:USDT"
      self.type = type.lower()
      self.side = side.lower()

      self.usd = usd  # USD
      self.coin_amount = coin_amount  # coin amount

      self.leverage = leverage

      self.price = price

      self.id = id  # order id

      self.stopPrice = stopPrice
      self.takeProfit = takeProfit
      self.stopLoss = stopLoss

      self.params = {}


      self.get_order_type()
      #self._info = order


  def is_NewOrder(self):
    return self._status == 'NEW'
  
  def is_NewPosition(self, positions):
    return False if self._coin in positions.keys() else True
  
  
"""
  def createOrder ( self, symbol, type, side, amount, price = undefined, params = {}):
    # exchange.createOrder ( self, symbol, type, side, amount, price = undefined, params = {}):
    pass
  

// camelCaseNotation
exchange.createLimitSellOrder (symbol, amount, price, params)
exchange.createLimitBuyOrder (symbol, amount, price, params)

// underscore_notation
exchange.create_limit_sell_order (symbol, amount, price, params)
exchange.create_limit_buy_order (symbol, amount, price, params)

// using general createLimitOrder and side = 'buy' or 'sell'
exchange.createLimitOrder (symbol, side, amount, price, params)
exchange.create_limit_order (symbol, side, amount, price, params)

// using general createOrder, type = 'limit' and side = 'buy' or 'sell'
exchange.createOrder (symbol, 'limit', side, amount, price, params)
exchange.create_order (symbol, 'limit', side, amount, price, params)



// camelCaseNotation
  exchange.createMarketSellOrder (symbol, amount, params)
  exchange.createMarketBuyOrder (symbol, amount, params)

  // underscore_notation
  exchange.create_market_sell_order (symbol, amount, params)
  exchange.create_market_buy_order (symbol, amount, params)

  // using general createMarketOrder and side = 'buy' or 'sell'
  exchange.createMarketOrder (symbol, side, amount, params)
  exchange.create_market_order (symbol, side, amount, params)

  // using general createOrder, type = 'market' and side = 'buy' or 'sell'
  exchange.createOrder (symbol, 'market', side, amount, ...)
  exchange.create_order (symbol, 'market', side, amount, ...)

symbol = 'ETH/BTC'
type = 'limit'  # or 'market'
side = 'sell'
amount = 123.45  # your amount
price = 54.321  # your price
params = {
    'triggerPrice': 123.45,  # your stop price
}
order = exchange.create_order(symbol, type, side, amount, price, params)


# for a stop loss order
params = {
    'stopLossPrice': 55.45,  # your stop loss price
}

# for a take profit order
params = {
    'takeProfitPrice': 120.45,  # your take profit price
}

order = exchange.create_order (symbol, type, side, amount, price, params)


# Python
symbol = 'ETH/BTC'
type = 'limit'  # or 'market'
side = 'buy'
amount = 123.45  # your amount
price = 115.321  # your price
params = {
    'stopLoss': {
        'type': 'limit', # or 'market'
        'price': 100.33,
        'stopLossPrice': 101.25,
    },
    'takeProfit': {
        'type': 'market',
        'takeProfitPrice': 150.75,
    }
}
order = exchange.create_order (symbol, type, side, amount, price, params)

bitfinex.createLimitSellOrder ('BTC/USD', 1, 10, { 'type': 'trailing-stop' })
"""

class TResults( T.mash ):
  
  def __init__(self):
    super().__init__()
    self.exchange = {}

    self.balance = {}
    self.pos = {}
    self.c_pos = {}
    self.orders = {}
    self.n_orders = {}
    self.c_orders = {}

