# -*- coding: utf-8 -*-

import os
import sys
from Tools import tools
from pprint import pprint
from base_exchange import base_Exchange, Position, Order

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import asyncio
#import ccxt  # noqa: E402
#import ccxt.pro as ccxt
import ccxt.async_support as ccxt  # noqa: E402

class bybit_Exchange_pro( base_Exchange ):

    def __init__(self, exchange_name, cfg_Jdata ):

        super().__init__( exchange_name, cfg_Jdata )
        #self.client = Client(self.apiKey, self.apiSecret)

        self._cl_name = self.__class__.__name__

    async def setMarket(self, market='spot'):
        self._exchange.options['defaultType'] = market   #  swap   very important set swap as default type
        self._markets = await self._exchange.load_markets(True)

    def connect_pub(self, demo=None):
        self._exchange = ccxt.bybit()

    async def connect( self, demo=None, market='swap' ):
    
        self._exchange = ccxt.bybit( {'apiKey': self._apiKey, 'secret': self._apiSecret } )
        #self._exchange = ccxt.bybit( {'apiKey': "Zt8m2AAyAlken7p4uE", 'secret': "vjGDG3HhyNSrslPYKCPby09mdU8UwuHzjg4q" } )
        #self._exchange = ccxt.bybit( {'apiKey': "", 'secret': "vjGDG3HhyNSrslPYKCPby09mdU8UwuHzjg4q" } )
        self._exchange.options['defaultType'] = market  # spot, swap, features, option

        if demo:
            self._demo = True
            self._exchange.set_sandbox_mode( True )
            self._exchange.enableDemoTrading ([True])

        self._markets = await self._exchange.load_markets() # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        #self._exchange.verbose = True  # uncomment for debugging

    def getOrder(self, symbol="", type="market", side='buy', amount=0, price=None):
        return {
        "id"     : 0,
        "symbol" : symbol,
        "type"   : type,
        "side"   : side,
        "amount" : amount,
        "price"  : None if type == 'market' else price
        }

    async def openOrder(self, order):
        create_order = await self._exchange.create_order(order['symbol'], order['type'], order['side'], order['amount'], order['price'])
        order['id'] = create_order['id']
        print('Create order id:', create_order['id'])

    async def openMarketOrder(self, order):
        # create market order and open position
        """symbol = 'LTC/USDT:USDT'
        type = 'market'
        side = 'buy'
        amount = 0.1
        price = None"""
        create_order = await self._exchange.create_order(order['symbol'], 'market', order['side'], order['amount'], None )
        order['id'] = create_order['id']
        print('Create order id:', create_order['id'])

    async def openLimitOrder(self, order):
        """symbol = 'LTC/USDT:USDT'
        type = 'limit'
        side = 'buy'
        amount = 0.1
        price = 200"""
        create_order = await self._exchange.create_order(order['symbol'], 'limit', order['side'], order['amount'], order['price'])
        order['id'] = create_order['id']
        print('Create order id:', create_order['id'])


    async def closeOrder(self):
        # Close position by issuing a order in the opposite direction
        side = 'sell'
        params = {
            'reduce_only': True
        }
        close_position_order = await self._exchange.createOrder(symbol, type, side, amount, price, params)
        print(close_position_order)

    def cancelOrders(self, symbol, param ):
        if type( param ) == dict:
            # cancell all open stop-orders
            # param = { 'stop': True }
            canceled_order = self._exchange.cancel_all_orders(symbol, param )
        else:
            # cancel created order
            canceled_order = self._exchange.cancel_order(param, symbol)

        print(canceled_order)

    async def checkOpenOrders(self, symbol, param=None):
        # Check canceled orders (bybit does not have a single endpoint to check orders
        # we have to choose whether to check open or closed orders and call fetch_open_orders
        # or fetch_closed_orders respectively
        if param is None:
            orders = await self._exchange.fetch_open_orders(symbol)
        else:
            # check opened stop-order
            # param = { 'stop': True }
            orders = await self._exchange.fetch_open_orders(symbol, None, None, param)

        print(orders)

    async def checkClosedOrders(self, symbol, param=None):
        # Check canceled orders (bybit does not have a single endpoint to check orders
        # we have to choose whether to check open or closed orders and call fetch_open_orders
        # or fetch_closed_orders respectively
        if param is None:
            orders = await self._exchange.fetch_closed_orders(symbol)
        else:
            # check opened stop-order
            # param = { 'stop': True }
            orders = await self._exchange.fetch_closed_orders(symbol, None, None, param)

        print(orders)


    async def checkOpenPosition(self, symbol):
        # check opened position
        symbols = [ symbol ]
        positions = await self._exchange.fetch_positions(symbols)
        print(positions)





    async def get_balance( self, p = "swap"):
        # -----------------------------------------------------------------------------
        print('-------------------------- balance ------')
        balances = await self._exchange.fetch_balance( {'type':p} )
        #what <> 0:
        
        for coin, val in balances['total'].items():
            if val != 0:
                print ( coin )
                break
            
        for cc in balances['info']['result']['list']:
            if cc['coin'] == coin:
                print( cc )
            
        #print(  balances )
        print('-------------------------- balance end ------')
      
      
    async def get_derivatives_balance(self, params={}):
      
        balances = await self._exchange.fetch_derivatives_balance( params )

        for balance in balances['result']['list']:
          print( balance )

        print ( balances )
      

    def get_open_positions( self):
        tools.dump(tools.green(self._exchange.id), 'fetching positions...')
        
        positions = self._exchange.fetch_positions()  # [ symbol ], params)
        
        for pos in positions:
          
            self._activePositions[ pos['info']['symbol'] ] = Position( pos )
            """
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
            """
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


    def get_open_orders( self, symbol=None, since=None, limit=None, params={}):
        
        self.get_derivatives_open_orders( symbol, since, limit, params)
        
        
    def get_derivatives_open_orders( self, symbol=None, since=None, limit=None, params={}):

        orders = self._exchange.fetch_derivatives_open_orders( symbol, since, limit, params)

        for order in orders:
          new_order = Bybit_Order( order )
          self._activeOrders[order['info']['symbol']] = new_order
          
          if new_order.is_NewPosition( self._activePositions):
            # execute
            pass
       
          
          
        #orders = self.exchange.fetch_derivatives_orders( symbol, since, limit, params)
        #orders2 = self.exchange.fetch_derivatives_orders( symbol, since, limit, params)

        #trades = self.exchange.fetch_derivatives_trades( symbol, since=None, limit=None, params={}):
        #trades = self.exchange.fetch_derivatives_trades( symbol, since, limit, params )

        kk = 9


class Bybit_Order(Order):
    """
    {'info':
       {'symbol': 'LINKUSDT',
        'orderId': 'aef99133-045b-4396-9e7c-b84001f3af9f',
        'side': 'Buy',
        'orderType': 'Market',
        'stopOrderType': 'PartialTakeProfit',
        'price': '0.000',
        'qty': '24.0',
        'timeInForce': 'ImmediateOrCancel',
        'orderStatus': 'Untriggered',
        'triggerPrice': '6.889',
        'orderLinkId': '',
        'createdTime': '1677362195513',
        'updatedTime': '1677362195513',
        'takeProfit': '0.000',
        'stopLoss': '0.000',
        'tpTriggerBy': 'UNKNOWN',
        'slTriggerBy': 'UNKNOWN',
        'triggerBy': 'LastPrice',
        'reduceOnly': True,
        'leavesQty': '24.0',
        'leavesValue': '0',
        'cumExecQty': '0.0',
        'cumExecValue': '0',
        'cumExecFee': '0',
        'triggerDirection': '2',
        'cancelType': 'UNKNOWN',
        'lastPriceOnCreated': '',
        'iv': '',
        'closeOnTrigger': True
        },
     'id': 'aef99133-045b-4396-9e7c-b84001f3af9f',
     'clientOrderId': None,
     'timestamp': 1677362195513,
     'datetime': '2023-02-25T21:56:35.513Z',
     'lastTradeTimestamp': None,
     'symbol': 'LINK/USDT:USDT',
     'type': 'market',
     'timeInForce': 'IOC',
     'postOnly': False,
     'side': 'buy',
     'price': None,
     'stopPrice': 6.889,
     'triggerPrice': 6.889,
     'amount': 24.0,
     'cost': 0.0,
     'average': None,
     'filled': 0.0,
     'remaining': 24.0,
     'status': 'open',
     'fee': {'cost': 0.0, 'currency': 'USDT'},
     'trades': [],
     'fees': [{'cost': 0.0, 'currency': 'USDT'}],
     'reduceOnly': None
     }"""
    
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
        self._status = self.info.status
        self._type = self.info.type
        self._closePosition = self.info.closePosition
        self._side = self.info.side  # buy/sell
        self._time = self.info.time
        self._updatetime = self.info.updatetime