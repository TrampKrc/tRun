# -*- coding: utf-8 -*-

import os
import sys

import ccxt as ccxt  # noqa: E402
from ccxt.base.types import Balances, Currency, Greeks, Int, Leverage, Market, MarketInterface, Num, Option, OptionChain, Order, OrderBook, OrderRequest, OrderSide, OrderType, Str, Strings, Ticker, Tickers, Trade, Transaction, TransferEntry
from typing import List
from pprint import pprint


import tools as T
from base_exchange import base_Exchange, Position, base_Order

#root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(root + '/python')

class yk_Bybit(base_Exchange):

    def __init__(self, exchange_name, cfg_Jdata ):

        super().__init__( exchange_name, cfg_Jdata )
        #self.client = Client(self.apiKey, self.apiSecret)

        self._cl_name = self.__class__.__name__

    def setMarket(self, market='spot'):
        self._exchange.options['defaultType'] = market   #  swap   very important set swap as default type
        self._markets = self._exchange.load_markets(True)

    def connect_pub(self, demo=None):
        self._exchange = ccxt.bybit()
    
    def connect( self, demo=None, market='swap' ):
    
        self._exchange = ccxt.bybit( {'apiKey': self._apiKey, 'secret': self._apiSecret, 'verbose':True, 'password':"kuvshinka" } )
        self._exchange.options['defaultType'] = market  # spot, swap, features, option
        # move to sandbox
        self._exchange.urls['api'] = self._exchange.urls['test']

        #print(self._exchange.fetch_balance())

        self._exchange.options['defaultType'] = market  # spot, swap, features, option

        dd = self._exchange.is_unified_enabled()

        if demo:
            self._demo = True
            self._exchange.set_sandbox_mode( True )
            #self._exchange.ena

        self._markets = self._exchange.load_markets() # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        #self._exchange.verbose = True  # uncomment for debugging

    def get_balance(self):
        # -----------------------------------------------------------------------------
        print('-------------------------- balance ------')
        balances = self._exchange.fetch_balance()
        # what <> 0:

        for coin, val in balances['total'].items():
            if val != 0:
                print(coin, val)


        #for cc in balances['info']['result']['list']:
        #    if cc['coin'] == coin:
        #        print(cc)

        print('-------------------------- balance end ------')

    # Check methods:

    def FetchOpenOrder(self, id: str, symbol: str = None, params={}):
        """
        :param str id: order id
        :param str [symbol]: unified symbol of the market the order was made in
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param boolean [params.stop]: set to True for fetching an open stop order
        :param str [params.type]: market type, ['swap', 'option', 'spot']
        :param str [params.subType]: market subType, ['linear', 'inverse']
        :param str [params.baseCoin]: Base coin. Supports linear, inverse & option
        :param str [params.settleCoin]: Settle coin. Supports linear, inverse & option
        :param str [params.orderFilter]: 'Order' or 'StopOrder' or 'tpslOrder'
        """
        return self._exchange.fetch_open_order(id, symbol, params)

    def FetchOpenOrders(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        """
        fetch all unfilled currently open orders
        :see: https://bybit-exchange.github.io/docs/v5/order/open-order
        :param str symbol: unified market symbol
        :param int [since]: the earliest time in ms to fetch open orders for
        :param int [limit]: the maximum number of open orders structures to retrieve
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param boolean [params.stop]: set to True for fetching open stop orders
        :param str [params.type]: market type, ['swap', 'option', 'spot']
        :param str [params.subType]: market subType, ['linear', 'inverse']
        :param str [params.baseCoin]: Base coin. Supports linear, inverse & option
        :param str [params.settleCoin]: Settle coin. Supports linear, inverse & option
        :param str [params.orderFilter]: 'Order' or 'StopOrder' or 'tpslOrder'
        :returns Order[]: a list of `order structures <https://docs.ccxt.com/#/?id=order-structure>`
        """
        return self._exchange.fetch_open_orders(symbol, since, limit, params)
        """
     [
        {'info': 
            {
                'symbol': 'BTCUSDT', 
                'orderType': 'Market', 
                'orderLinkId': '', 'slLimitPrice': '0', 
                'orderId': 'e1366292-ffc9-4d5e-9849-9026880748a7', 
                'cancelType': 'UNKNOWN', 'avgPrice': '', 'stopOrderType': 'TakeProfit', 
                'lastPriceOnCreated': '57268.3', 'orderStatus': 'Untriggered', 
                'createType': 'CreateByTakeProfit', 
                'takeProfit': '', 'cumExecValue': '0', 'tpslMode': 'Full', 'smpType': 'None', 
                'triggerDirection': '1', 'blockTradeId': '', 'isLeverage': '', 'rejectReason': 'EC_NoError', 
                'price': '0', 'orderIv': '', 'createdTime': '1720746278254', 'tpTriggerBy': '', 'positionIdx': '0', 'timeInForce': 'IOC', 'leavesValue': '0', 
                'updatedTime': '1720746957199', 'side': 'Sell', 'smpGroup': '0', 'triggerPrice': '57601.6', 'tpLimitPrice': '0', 'cumExecFee': '0', 
                'leavesQty': '0.002', 'slTriggerBy': '', 'closeOnTrigger': True, 'placeType': '', 'cumExecQty': '0', 
                'reduceOnly': True, 'qty': '0.002', 'stopLoss': '', 'marketUnit': '', 'smpOrderId': '', 
                'triggerBy': 'LastPrice', 
                'nextPageCursor': 'e1366292-ffc9-4d5e-9849-9026880748a7%3A1720746278254%2Ce1366292-ffc9-4d5e-9849-9026880748a7%3A1720746278254'
            },

            'id': 'e1366292-ffc9-4d5e-9849-9026880748a7', 
            'clientOrderId': None, 'timestamp': 1720746278254, 'datetime': '2024-07-12T01:04:38.254Z', 'lastTradeTimestamp': 1720746957199, 
            'lastUpdateTimestamp': 1720746957199, 
            'symbol': 'BTC/USDT:USDT', 'type': 'market', 'timeInForce': 'IOC', 
            'postOnly': False, 'reduceOnly': True, 'side': 'sell', 'price': None, 'stopPrice': 57601.6, 
            'triggerPrice': 57601.6, 'takeProfitPrice': 57601.6, 'stopLossPrice': None, 
            'amount': 0.002, 'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.002, 
            'status': 'open', 
            'fee': {'cost': '0', 'currency': 'USDT'}, 
            'trades': [], 
            'fees': [{'cost': 0.0, 'currency': 'USDT'}]
        }
    ]
    
    have 4 open orders
    [
        {'info': 
            {'symbol': 'BTCUSDT', 'orderType': 'Market', 'orderLinkId': '', 'slLimitPrice': '0', 'orderId': 'c34ae9a1-9e37-47e5-a6c2-83003db9799b', 'cancelType': 'UNKNOWN', 'avgPrice': '', 
             'stopOrderType': 'PartialTakeProfit', 'lastPriceOnCreated': '63259', 'orderStatus': 'Untriggered', 
             'createType': 'CreateByPartialTakeProfit', 'takeProfit': '', 'cumExecValue': '0', 'tpslMode': 'Partial', 'smpType': 'None', 'triggerDirection': '1', 'blockTradeId': '', 'isLeverage': '', 'rejectReason': 'EC_NoError', 'price': '0', 'orderIv': '', 'createdTime': '1721074472015', 'tpTriggerBy': '', 'positionIdx': '0', 'timeInForce': 'IOC', 'leavesValue': '0', 'updatedTime': '1721074472015', 'side': 'Sell', 'smpGroup': '0', 
             'triggerPrice': '63760', 'tpLimitPrice': '0', 'cumExecFee': '0', 'leavesQty': '0.3', 'slTriggerBy': '', 'closeOnTrigger': True, 'placeType': '', 'cumExecQty': '0', 'reduceOnly': True, 'qty': '0.3', 'stopLoss': '', 'marketUnit': '', 'smpOrderId': '', 'triggerBy': 'LastPrice'
            },
            'id': 'c34ae9a1-9e37-47e5-a6c2-83003db9799b', 'clientOrderId': None, 'timestamp': 1721074472015, 'datetime': '2024-07-15T20:14:32.015Z', 'lastTradeTimestamp': 1721074472015, 'lastUpdateTimestamp': 1721074472015, 'symbol': 'BTC/USDT:USDT', 'type': 'market', 'timeInForce': 'IOC', 'postOnly': False, 'reduceOnly': True, 'side': 'sell', 'price': None, 
            'stopPrice': 63760.0, 'triggerPrice': 63760.0, 
    TP0     'takeProfitPrice': 63760.0, 'stopLossPrice': None, 'amount': 0.3, 'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.3, 'status': 'open', 
            'fee': {'cost': '0', 'currency': 'USDT'}, 'trades': [], 'fees': [{'cost': 0.0, 'currency': 'USDT'}]
       }, 
            
       {'info': 
            {'symbol': 'BTCUSDT', 'orderType': 'Market', 'orderLinkId': '', 'slLimitPrice': '0', 
             'orderId': '785305dc-2a5f-4bd5-a5b7-b2b643682cfd', 'cancelType': 'UNKNOWN', 'avgPrice': '', 
             'stopOrderType': 'PartialStopLoss', 'lastPriceOnCreated': '63259', 'orderStatus': 'Untriggered', 
             'createType': 'CreateByPartialStopLoss', 'takeProfit': '', 'cumExecValue': '0', 'tpslMode': 'Partial', 'smpType': 'None', 'triggerDirection': '2', 'blockTradeId': '', 'isLeverage': '', 'rejectReason': 'EC_NoError', 'price': '0', 'orderIv': '', 
             'createdTime': '1721074472015', 'tpTriggerBy': '', 'positionIdx': '0', 'timeInForce': 'IOC', 'leavesValue': '0', 'updatedTime': '1721074472015', 'side': 'Sell', 'smpGroup': '0', 
             'triggerPrice': '62760', 'tpLimitPrice': '0', 'cumExecFee': '0', 'leavesQty': '0.3', 'slTriggerBy': '', 'closeOnTrigger': True, 'placeType': '', 'cumExecQty': '0', 'reduceOnly': True, 
             'qty': '0.3', 'stopLoss': '', 'marketUnit': '', 'smpOrderId': '', 'triggerBy': 'LastPrice'
            }, 
            'id': '785305dc-2a5f-4bd5-a5b7-b2b643682cfd', 'clientOrderId': None, 'timestamp': 1721074472015, 
            'datetime': '2024-07-15T20:14:32.015Z', 'lastTradeTimestamp': 1721074472015, 'lastUpdateTimestamp': 1721074472015, 
            'symbol': 'BTC/USDT:USDT', 'type': 'market', 'timeInForce': 'IOC', 'postOnly': False, 'reduceOnly': True, 'side': 'sell', 'price': None, 
            'stopPrice': 62760.0, 'triggerPrice': 62760.0, 
    SL0     'takeProfitPrice': None, 'stopLossPrice': 62760.0, 'amount': 0.3, 
            'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.3, 'status': 'open', 'fee': {'cost': '0', 'currency': 'USDT'}, 'trades': [], 'fees': [{'cost': 0.0, 'currency': 'USDT'}]
       },
        
       {'info': 
           {'symbol': 'BTCUSDT', 'orderType': 'Market', 'orderLinkId': '', 'slLimitPrice': '0', 'orderId': 'faf5f121-13bd-4f7f-b5ae-4efe89bbbdfa', 'cancelType': 'UNKNOWN', 'avgPrice': '', 'stopOrderType': 'PartialTakeProfit', 'lastPriceOnCreated': '63259.1', 'orderStatus': 'Untriggered', 
            'createType': 'CreateByPartialTakeProfit', 'takeProfit': '', 'cumExecValue': '0', 'tpslMode': 'Partial', 'smpType': 'None', 'triggerDirection': '1', 'blockTradeId': '', 'isLeverage': '', 'rejectReason': 'EC_NoError', 'price': '0', 'orderIv': '', 'createdTime': '1721074473060', 'tpTriggerBy': '', 'positionIdx': '0', 'timeInForce': 'IOC', 'leavesValue': '0', 'updatedTime': '1721074473060', 'side': 'Sell', 'smpGroup': '0', 'triggerPrice': '63560', 'tpLimitPrice': '0', 'cumExecFee': '0', 'leavesQty': '0.15', 'slTriggerBy': '', 'closeOnTrigger': True, 'placeType': '', 'cumExecQty': '0', 'reduceOnly': True, 'qty': '0.15', 'stopLoss': '', 'marketUnit': '', 'smpOrderId': '', 'triggerBy': 'LastPrice'
           },
           'id': 'faf5f121-13bd-4f7f-b5ae-4efe89bbbdfa', 'clientOrderId': None, 'timestamp': 1721074473060, 'datetime': '2024-07-15T20:14:33.060Z', 'lastTradeTimestamp': 1721074473060, 'lastUpdateTimestamp': 1721074473060, 'symbol': 'BTC/USDT:USDT', 'type': 'market', 'timeInForce': 'IOC', 'postOnly': False, 'reduceOnly': True, 'side': 'sell', 'price': None, 
           'stopPrice': 63560.0, 'triggerPrice': 63560.0, 
    TP1    'takeProfitPrice': 63560.0, 'stopLossPrice': None, 'amount': 0.15, 
           'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.15, 'status': 'open', 'fee': {'cost': '0', 'currency': 'USDT'}, 'trades': [], 'fees': [{'cost': 0.0, 'currency': 'USDT'}]
       },
        
       {'info': 
           {'symbol': 'BTCUSDT', 'orderType': 'Market', 'orderLinkId': '', 'slLimitPrice': '0', 'orderId': '51de0cea-2616-432c-8481-edf182f32a14', 'cancelType': 'UNKNOWN', 'avgPrice': '', 'stopOrderType': 'PartialTakeProfit', 'lastPriceOnCreated': '63259.1', 'orderStatus': 'Untriggered', 
            'createType': 'CreateByPartialTakeProfit', 'takeProfit': '', 'cumExecValue': '0', 'tpslMode': 'Partial', 'smpType': 'None', 'triggerDirection': '1', 'blockTradeId': '', 'isLeverage': '', 'rejectReason': 'EC_NoError', 'price': '0', 'orderIv': '', 'createdTime': '1721074474112', 'tpTriggerBy': '', 'positionIdx': '0', 'timeInForce': 'IOC', 'leavesValue': '0', 'updatedTime': '1721074474112', 'side': 'Sell', 'smpGroup': '0', 'triggerPrice': '63660', 'tpLimitPrice': '0', 'cumExecFee': '0', 'leavesQty': '0.3', 'slTriggerBy': '', 'closeOnTrigger': True, 'placeType': '', 'cumExecQty': '0', 'reduceOnly': True, 'qty': '0.3', 'stopLoss': '', 'marketUnit': '', 'smpOrderId': '', 'triggerBy': 'LastPrice', 'nextPageCursor': '51de0cea-2616-432c-8481-edf182f32a14%3A1721074474112%2C785305dc-2a5f-4bd5-a5b7-b2b643682cfd%3A1721074472015'
           }, 
           'id': '51de0cea-2616-432c-8481-edf182f32a14', 'clientOrderId': None, 'timestamp': 1721074474112, 'datetime': '2024-07-15T20:14:34.112Z', 'lastTradeTimestamp': 1721074474112, 'lastUpdateTimestamp': 1721074474112, 'symbol': 'BTC/USDT:USDT', 'type': 'market', 'timeInForce': 'IOC', 'postOnly': False, 'reduceOnly': True, 'side': 'sell', 'price': None, 
           'stopPrice': 63660.0, 'triggerPrice': 63660.0, 
    TP2    'takeProfitPrice': 63660.0, 'stopLossPrice': None, 'amount': 0.3, 'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.3, 'status': 'open', 
           'fee': {'cost': '0', 'currency': 'USDT'}, 'trades': [], 'fees': [{'cost': 0.0, 'currency': 'USDT'}]
       }
    ]
        """

    def __tt1(self):
        symbol = ""
        param = {}
        # Check canceled orders (bybit does not have a single endpoint to check orders
        # we have to choose whether to check open or closed orders and call fetch_open_orders
        # or fetch_closed_orders respectively
        if param is None:
            orders = self._exchange.fetch_open_orders(symbol)
        else:
            # check opened stop-order
            # param = { 'stop': True }
            orders = self._exchange.fetch_open_orders(symbol, None, None, param)

        print(orders)


    def __tt2(self):
        symbol = ""
        param = {}
        # Check canceled orders (bybit does not have a single endpoint to check orders
        # we have to choose whether to check open or closed orders and call fetch_open_orders
        # or fetch_closed_orders respectively
        if param is None:
            orders = self._exchange.fetch_closed_orders(symbol)
        else:
            # check opened stop-order
            # param = { 'stop': True }
            orders = self._exchange.fetch_closed_orders(symbol, None, None, param)

        print(orders)


    def FetchClosedOrder(self, id: str, symbol: Str = None, params={}):
        """
        fetches information on a closed order made by the user
        :see: https://bybit-exchange.github.io/docs/v5/order/order-list
        :param str id: order id
        :param str [symbol]: unified symbol of the market the order was made in
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param boolean [params.stop]: set to True for fetching a closed stop order
        :param str [params.type]: market type, ['swap', 'option', 'spot']
        :param str [params.subType]: market subType, ['linear', 'inverse']
        :param str [params.orderFilter]: 'Order' or 'StopOrder' or 'tpslOrder'
        :returns dict: an `order structure <https://docs.ccxt.com/#/?id=order-structure>`
        """
        return self._exchange.fetch_closed_order(id, symbol, params)

    def FetchClosedOrders(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        """
        fetches information on multiple closed orders made by the user
        :see: https://bybit-exchange.github.io/docs/v5/order/order-list
        :param str [symbol]: unified market symbol of the market orders were made in
        :param int [since]: the earliest time in ms to fetch orders for
        :param int [limit]: the maximum number of order structures to retrieve
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param boolean [params.stop]: set to True for fetching closed stop orders
        :param str [params.type]: market type, ['swap', 'option', 'spot']
        :param str [params.subType]: market subType, ['linear', 'inverse']
        :param str [params.orderFilter]: 'Order' or 'StopOrder' or 'tpslOrder'
        :param int [params.until]: the latest time in ms to fetch entries for
        :param boolean [params.paginate]: default False, when True will automatically paginate by calling self endpoint multiple times. See in the docs all the [available parameters](https://github.com/ccxt/ccxt/wiki/Manual#pagination-params)
        :returns Order[]: a list of `order structures <https://docs.ccxt.com/#/?id=order-structure>`
        """
        return self._exchange.fetch_closed_orders(symbol, since, limit, params)
        """
        [
          {'info': 
              { 'symbol': 'BTCUSDT', 'orderType': 'Market', 'orderLinkId': '', 'slLimitPrice': '0', 
                'orderId': '49d07a7a-fc27-458f-8a88-18b262526a1c', 'cancelType': 'UNKNOWN', 
                'avgPrice': '57174', 'stopOrderType': '', 'lastPriceOnCreated': '57174', 'orderStatus': 'Filled', 'createType': 'CreateByUser', 'takeProfit': '', 'cumExecValue': '57.174', 'tpslMode': '', 'smpType': 'None', 'triggerDirection': '0', 'blockTradeId': '', 'rejectReason': 'EC_NoError', 'isLeverage': '', 'price': '60032.7', 'orderIv': '', 'createdTime': '1720745966515', 'tpTriggerBy': '', 'positionIdx': '0', 'timeInForce': 'IOC', 'leavesValue': '0', 'updatedTime': '1720745966515', 'side': 'Buy', 'smpGroup': '0', 'triggerPrice': '', 'tpLimitPrice': '0', 'cumExecFee': '0.0314457', 'slTriggerBy': '', 
                'leavesQty': '0', 'closeOnTrigger': False, 'placeType': '', 'cumExecQty': '0.001', 
                'reduceOnly': False, 
                'qty': '0.001', 'stopLoss': '', 'smpOrderId': '', 'triggerBy': ''
              },

             'id': '49d07a7a-fc27-458f-8a88-18b262526a1c', 'clientOrderId': None, 
               'timestamp': 1720745966515, 'datetime': '2024-07-12T00:59:26.515Z', 
               'lastTradeTimestamp': 1720745966515, 'lastUpdateTimestamp': 1720745966515, 
               'symbol': 'BTC/USDT:USDT', 
               'type': 'market', 'timeInForce': 'IOC', 'postOnly': False, 'reduceOnly': False, 
               'side': 'buy', 'price': 60032.7, 'stopPrice': None, 'triggerPrice': None, 
               'takeProfitPrice': None, 'stopLossPrice': None, 'amount': 0.001, 'cost': 57.174, 'average': 57174.0, 'filled': 0.001, 'remaining': 0.0, 
               'status': 'closed', 
               'fee': {'cost': '0.0314457', 'currency': 'USDT'}, 'trades': [], 
               'fees': [{'cost': 0.0314457, 'currency': 'USDT'}]
          }, 
          {'info': 
              {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'orderLinkId': '', 'slLimitPrice': '0', 
               'orderId': '75cb2b41-136f-4845-b2cf-6da7b7748f18', 'cancelType': 'UNKNOWN', 
               'avgPrice': '56894', 'stopOrderType': '', 'lastPriceOnCreated': '56934.1', 'orderStatus': 'Filled', 'createType': 'CreateByUser', 'takeProfit': '', 'cumExecValue': '56.894', 'tpslMode': '', 'smpType': 'None', 'triggerDirection': '0', 'blockTradeId': '', 'rejectReason': 'EC_NoError', 'isLeverage': '', 'price': '56894', 'orderIv': '', 'createdTime': '1720746955499', 'tpTriggerBy': '', 'positionIdx': '0', 'timeInForce': 'GTC', 'leavesValue': '0', 'updatedTime': '1720746957199', 'side': 'Buy', 'smpGroup': '0', 'triggerPrice': '', 'tpLimitPrice': '0', 'cumExecFee': '0.0113788', 'slTriggerBy': '', 'leavesQty': '0', 
               'closeOnTrigger': False, 'placeType': '', 'cumExecQty': '0.001', 'reduceOnly': False, 
               'qty': '0.001', 'stopLoss': '', 'smpOrderId': '', 'triggerBy': '', 
               'nextPageCursor': '75cb2b41-136f-4845-b2cf-6da7b7748f18%3A1720746955499%2C49d07a7a-fc27-458f-8a88-18b262526a1c%3A1720745966515'
              },

              'id': '75cb2b41-136f-4845-b2cf-6da7b7748f18', 'clientOrderId': None, 'timestamp': 1720746955499, 
               'datetime': '2024-07-12T01:15:55.499Z', 'lastTradeTimestamp': 1720746957199, 
               'lastUpdateTimestamp': 1720746957199, 'symbol': 'BTC/USDT:USDT', 'type': 'limit', 
               'timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': False, 'side': 'buy', 
               'price': 56894.0, 
               'stopPrice': None, 'triggerPrice': None, 'takeProfitPrice': None, 'stopLossPrice': None, 
               'amount': 0.001, 'cost': 56.894, 'average': 56894.0, 'filled': 0.001, 'remaining': 0.0, 
               'status': 'closed', 
               'fee': {'cost': '0.0113788', 'currency': 'USDT'}, 'trades': [], 
               'fees': [{'cost': 0.0113788, 'currency': 'USDT'}]
          }
        ]
        """

    def FetchCanceledOrders(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        """
        fetches information on multiple canceled orders made by the user
        :see: https://bybit-exchange.github.io/docs/v5/order/order-list
        :param str [symbol]: unified market symbol of the market orders were made in
        :param int [since]: timestamp in ms of the earliest order, default is None
        :param int [limit]: max number of orders to return, default is None
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param boolean [params.stop]: True if stop order
        :param str [params.type]: market type, ['swap', 'option', 'spot']
        :param str [params.subType]: market subType, ['linear', 'inverse']
        :param str [params.orderFilter]: 'Order' or 'StopOrder' or 'tpslOrder'
        :param int [params.until]: the latest time in ms to fetch entries for
        :param boolean [params.paginate]: default False, when True will automatically paginate by calling self endpoint multiple times. See in the docs all the [available parameters](https://github.com/ccxt/ccxt/wiki/Manual#pagination-params)
        :returns dict: a list of `order structures <https://docs.ccxt.com/#/?id=order-structure>`
        """
        return self._exchange.fetch_canceled_orders(symbol, since, limit, params)

    def FetchCanceledClosedOrders(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}) -> \
        List[Order]:
        """
        fetches information on multiple canceled and closed orders made by the user
        :see: https://bybit-exchange.github.io/docs/v5/order/order-list
        :param str [symbol]: unified market symbol of the market orders were made in
        :param int [since]: the earliest time in ms to fetch orders for
        :param int [limit]: the maximum number of order structures to retrieve
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param boolean [params.stop]: set to True for fetching stop orders
        :param str [params.type]: market type, ['swap', 'option', 'spot']
        :param str [params.subType]: market subType, ['linear', 'inverse']
        :param str [params.orderFilter]: 'Order' or 'StopOrder' or 'tpslOrder'
        :param int [params.until]: the latest time in ms to fetch entries for
        :param boolean [params.paginate]: default False, when True will automatically paginate by calling self endpoint multiple times. See in the docs all the [available parameters](https://github.com/ccxt/ccxt/wiki/Manual#pagination-params)
        :returns Order[]: a list of `order structures <https://docs.ccxt.com/#/?id=order-structure>`
        """
        return self._exchange.fetch_canceled_and_closed_orders(symbol, since, limit, params)

    def FetchMyTrades(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        """
        fetch all trades made by the user
        :see: https://bybit-exchange.github.io/docs/api-explorer/v5/position/execution
        :param str symbol: unified market symbol
        :param int [since]: the earliest time in ms to fetch trades for
        :param int [limit]: the maximum number of trades structures to retrieve
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param str [params.type]: market type, ['swap', 'option', 'spot']
        :param str [params.subType]: market subType, ['linear', 'inverse']
        :param boolean [params.paginate]: default False, when True will automatically paginate by calling self endpoint multiple times. See in the docs all the [availble parameters](https://github.com/ccxt/ccxt/wiki/Manual#pagination-params)
        :returns Trade[]: a list of `trade structures <https://docs.ccxt.com/#/?id=trade-structure>`
        """
        orders = self._exchange.fetch_my_trades(symbol, since, limit, params)
        return orders

    def FetchTrades(self, symbol: str, since: Int = None, limit: Int = None, params={}) -> List[Trade]:
        """
        get the list of most recent trades for a particular symbol
        :see: https://bybit-exchange.github.io/docs/v5/market/recent-trade
        :param str symbol: unified symbol of the market to fetch trades for
        :param int [since]: timestamp in ms of the earliest trade to fetch
        :param int [limit]: the maximum amount of trades to fetch
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param str [params.type]: market type, ['swap', 'option', 'spot']
        :param str [params.subType]: market subType, ['linear', 'inverse']
        :returns Trade[]: a list of `trade structures <https://docs.ccxt.com/#/?id=public-trades>`
        """
        orders = self._exchange.fetch_trades(symbol, since, limit, params)
        return orders

    def FetchOrderTrades(self, id: str, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        """
        fetch all the trades made from a single order
        :see: https://bybit-exchange.github.io/docs/v5/position/execution
        :param str id: order id
        :param str symbol: unified market symbol
        :param int [since]: the earliest time in ms to fetch trades for
        :param int [limit]: the maximum number of trades to retrieve
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :returns dict[]: a list of `trade structures <https://docs.ccxt.com/#/?id=trade-structure>`
        """
        orders = self._exchange.fetch_order_trades(id, symbol, since, limit, params)
        # -- orders = self._exchange.fetch_trades()
        return orders

    def FetchOpenPosition(self, symbol: str, params={}):  # 'BTC/USDT:USDT'
        """
        fetch data on a single open contract trade position
        :see: https://bybit-exchange.github.io/docs/v5/position
        :param str symbol: unified market symbol of the market the position is held in, default is None
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :returns dict: a `position structure <https://docs.ccxt.com/#/?id=position-structure>`
        """
        return self._exchange.fetch_position(symbol, params)

    def FetchOpenPositions(self, symbols: Strings = None, params={}):
        """
        fetch all open positions
        :see: https://bybit-exchange.github.io/docs/v5/position
        :param str[] symbols: list of unified market symbols
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param str [params.type]: market type, ['swap', 'option', 'spot']
        :param str [params.subType]: market subType, ['linear', 'inverse']
        :param str [params.baseCoin]: Base coin. Supports linear, inverse & option
        :param str [params.settleCoin]: Settle coin. Supports linear, inverse & option
        :returns dict[]: a list of `position structure <https://docs.ccxt.com/#/?id=position-structure>`
        """
        return self._exchange.fetch_positions(symbols, params)
        """
            [{'info': {
                 'symbol': 'BTCUSDT', 'leverage': '10', 'autoAddMargin': '0', 'avgPrice': '57034', 'liqPrice': '',
                        'riskLimitValue': '2000000', 'takeProfit': '57601.6', 'positionValue': '114.068',
                        'isReduceOnly': False, 'tpslMode': 'Full', 'riskId': '1', 'trailingStop': '0',
                        'unrealisedPnl': '-0.32258', 'markPrice': '56872.71', 'adlRankIndicator': '2',
                        'cumRealisedPnl': '-3546.15975847', 'positionMM': '0.62680366', 'createdTime': '1717821325356',
                        'positionIdx': '0', 'positionIM': '11.46326366', 'seq': '520542080', 'updatedTime': '1720746957199',
                        'side': 'Buy', 'bustPrice': '', 'positionBalance': '0', 'leverageSysUpdatedTime': '',
                        'curRealisedPnl': '-0.0428245', 'size': '0.002', 'positionStatus': 'Normal',
                        'mmrSysUpdatedTime': '', 'stopLoss': '', 'tradeMode': '0', 'sessionAvgPrice': '',
                        'nextPageCursor': 'BTCUSDT%2C1720746957199%2C0'},

               'id': None, 'symbol': 'BTC/USDT:USDT',
               'timestamp': 1720746957199, 'datetime': '2024-07-12T01:15:57.199Z', 'lastUpdateTimestamp': None,
               'initialMargin': 11.46326366, 'initialMarginPercentage': 0.100495, 'maintenanceMargin': 0.62680366,
               'maintenanceMarginPercentage': 0.005495, 'entryPrice': 57034.0, 'notional': 114.068, 'leverage': 10.0,
               'unrealizedPnl': -0.32258, 'contracts': 0.002, 'contractSize': 1.0, 'marginRatio': None,
               'liquidationPrice': None, 'markPrice': 56872.71, 'lastPrice': None, 'collateral': 0.0, 'marginMode': None,
               'side': 'long', 'percentage': None, 'stopLossPrice': None, 
               'takeProfitPrice': 57601.6 
               }
               ]
            """

    def get_ticker_price(self, symbol: str):
        return self._exchange.fetch_ticker( symbol ) ['last']

    def FetchTickers(self):
        positions = self._exchange.fetch_tickers()



    def getOrder(self, symbol="", type="market", side='buy', amount=0, price=None, id='', stopPrice=None, takeProfit = None, stopLoss=None ):
        return {
        "id"     : id,
        "symbol" : symbol,
        "type"   : type,
        "side"   : side,
        "amount" : amount,
        "price"  : None if type == 'market' else price,
        "stopPrice": stopPrice,
        "takeProfit": takeProfit,
        "stopLoss":   stopLoss
        }

    def CreateOrders(self, order):
        # createOrders
        self._exchange.create_orders()

    def CreatePostOnlyOrder(self):
        self._exchange.create_post_only_order()

    def CreateReduceOnlyOrder(self, order, param={} ):
        return self._exchange.create_reduce_only_order( order['symbol'], order['type'], order['side'], order['amount'], order['price'], params=param )


    def CreateOrder(self, order, param={} ):
        created_order = self._exchange.create_order(order['symbol'], order['type'], order['side'], order['amount'], order['price'], params=param )
        order['id'] = created_order['id']
        print('Create order id:', created_order['id'])
        return created_order

    def CreateMarketOrder(self, order, param={} ):
        # create market order and open position
        """symbol = 'LTC/USDT:USDT'
        type = 'market'
        side = 'buy'
        amount = 0.1
        price = None"""
        create_order = self._exchange.create_order(order['symbol'], 'market', order['side'], order['amount'], params=param )
        order['id'] = create_order['id']
        print('Create order id:', create_order['id'])
        return order

    def CreateLimitOrder(self, order, param={} ):
        """
        symbol = 'LTC/USDT:USDT'
        type = 'limit'
        side = 'buy'
        amount = 0.1
        price = 200"""
        create_order = self._exchange.create_order(order['symbol'], 'limit', order['side'], order['amount'], order['price'], params=param )
        order['id'] = create_order['id']
        print('Create order id:', create_order['id'])
        return order

    # stopPrice -> triggerPrice -> triggeredOrder  -> exec with price
    # param['triggerDirection'] : 'above'(1) / 'below'(2)
    # open limit order buy -> stopPrice(triggerPrice) -> buy price;
    # triggerDirection = 'above'(1) -> stopPrice >= currrent price
    # triggerDirection = 'below'(2) -> stopPrice <= currrent price
    def CreateStopOrder(self, order, param={} ):
        return self._exchange.create_stop_order( order['symbol'], order['type'], order['side'], order['amount'], order['price'],order['stopPrice'], params=param )

    def CreateStopLimitOrder(self, order, param={} ):
        return self._exchange.create_stop_limit_order( order['symbol'], order['side'], order['amount'], order['price'],order['stopPrice'], params=param )

    def CreateStopMarketOrder(self, order, param={} ):
        return self._exchange.create_stop_market_order(order['symbol'], order['side'], order['amount'], order['stopPrice'], params=param)

    # takeProfit -> triggerPrice -> triggeredOrder  -> exec with price
    def CreateTakeProfitOrder(self, order, param={} ):
        return self._exchange.create_take_profit_order( order['symbol'], order['type'], order['side'], order['amount'], order['price'], order['takeProfit'], params=param )

    # stopLoss -> triggerPrice -> triggeredOrder -> exec with price
    def CreateStopLossOrder(self, order, param={} ):
        return self._exchange.create_stop_loss_order( order['symbol'], order['type'], order['side'], order['amount'], order['price'], order['stopLoss'], param )


# ord1=bybit.getOrder(sym1,type='limit',side='buy',amount=0.01,price=66800,takeProfit=67000, stopLoss=67000 )
# params = {'takeProfitAmount':0.05, 'stopLossAmount': 0.05 }
    def CreateOrder_SLTP(self, order, param={} ):
        """
        create an order with a stop loss or take profit attached(type 3)
        :param str symbol: unified symbol of the market to create an order in
        :param str type: 'market' or 'limit'
        :param str side: 'buy' or 'sell'
        :param float amount: how much you want to trade in units of the base currency or the number of contracts
        :param float [price]: the price to fulfill the order, in units of the quote currency, ignored in market orders
        :param float [takeProfit]: the take profit price, in units of the quote currency
        :param float [stopLoss]: the stop loss price, in units of the quote currency

        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param str [params.takeProfitType]: *not available on all exchanges* 'limit' or 'market'
        :param str [params.takeProfitPriceType]: *not available on all exchanges* 'last', 'mark' or 'index'
        :param float [params.takeProfitLimitPrice]: *not available on all exchanges* limit price for a limit take profit order
        :param float [params.takeProfitAmount]: *not available on all exchanges* the amount for a take profit

        :param str [params.stopLossType]: *not available on all exchanges* 'limit' or 'market'
        :param str [params.stopLossPriceType]: *not available on all exchanges* 'last', 'mark' or 'index'
        :param float [params.stopLossLimitPrice]: *not available on all exchanges* stop loss for a limit stop loss order
        :param float [params.stopLossAmount]: *not available on all exchanges* the amount for a stop loss
        :returns dict: an `order structure <https://docs.ccxt.com/#/?id=order-structure>`
        """
        return self._exchange.create_order_with_take_profit_and_stop_loss(
            order['symbol'], order['type'], order['side'], order['amount'],
            order['price'], order['takeProfit'], order['stopLoss'], params=param )

    def CreateOrder_SLTP2(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, takeProfit: Num = None, stopLoss: Num = None, param={} ):
        return self._exchange.create_order_with_take_profit_and_stop_loss(
            symbol, type, side, amount, price, takeProfit, stopLoss, params=param )

    def CreateTakeProfitandStopLoss2(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, takeProfit: Num = None, stopLoss: Num = None, param={} ):
        return self._exchange.create_take_profit_and_stop_loss( symbol, type, side, amount, price, params=param )


    # triggerPrice -> triggeredOrder
    # triggerDirection == 'above'(1) / 'below'(2)
    def CreateTriggerOrder(self, order, param={} ):
        self._exchange.create_trigger_order( order['symbol'], order['type'], order['side'], order['amount'], order['price'], order['triggerPrice'], param)

    def CreateStopTrailingPointOrder(self):
        self._exchange.create_trailing_amount_order()

    def CreateStopTrailingPercentOrder(self):
        self._exchange.create_trailing_percent_order()

    def EditOrder(self, order, param={} ):
        return self._exchange.edit_order( order['id'], order['symbol'], order['type'], order['side'], order['amount'], order['price'], params=param)

    def EditOrder2(self, id: str, symbol: str, type: OrderType, side: OrderSide, amount: Num = None, price: Num = None, param={}):
        return self._exchange.edit_order( id, symbol, type, side, amount, price, params=param )


    def closeOrder(self):
        # Close position by issuing a order in the opposite direction
        side = 'sell'
        params = {
            'reduce_only': True
        }
        #close_position_order = self._exchange.createOrder(symbol, type, side, amount, price, params)
        #print(close_position_order)

    def CancelOrder(self, order, param={} ):
        return  self._exchange.cancel_order( order['id'], order['symbol'], param)

    def CancelOrder2(self, id: str, symbol: Str = None, param={} ):
        return  self._exchange.cancel_order( id, symbol, param)

    def CancelOrders(self, symbol, param ):
        self._exchange.cancel_orders(param, symbol)

    def CancelAllOrders(self, symbol, param={} ):
        """
        cancel all open orders
        :see: https://bybit-exchange.github.io/docs/v5/order/cancel-all
        :param str symbol: unified market symbol, only orders in the market of self symbol are cancelled when symbol is not None
        :param dict [params]: extra parameters specific to the exchange API endpoint
        :param boolean [params.stop]: True if stop order
        :param str [params.type]: market type, ['swap', 'option', 'spot']
        :param str [params.subType]: market subType, ['linear', 'inverse']
        :param str [params.baseCoin]: Base coin. Supports linear, inverse & option
        :param str [params.settleCoin]: Settle coin. Supports linear, inverse & option
        :returns dict[]: a list of `order structures <https://docs.ccxt.com/#/?id=order-structure>`
        """
        return  self._exchange.cancel_all_orders(symbol, param)











      
    def get_derivatives_balance(self, params={}):
      
        balances = self._exchange.fetch_derivatives_balance( params )

        for balance in balances['result']['list']:
          print( balance )

        print ( balances )
      

    def get_open_positions( self):
        T.dump( T.green(self._exchange.id), 'fetching positions...')
        
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


    def read_positions(self, symbol=None ):
        positions = self._exchange.fetch_positions( symbol )  # [ symbol ], params)
        pprint(positions)

    """
    positions = [ pos, pos ]
    pos:
    {'info': {'symbol': 'BTCUSDT', 'leverage': '10', 'autoAddMargin': '0', 'avgPrice': '118794.74285714', 'liqPrice': '', 'riskLimitValue': '2000000', 'takeProfit': '', 'positionValue': '831.5632', 'isReduceOnly': False, 'tpslMode': 'Full', 'riskId': '1', 'trailingStop': '0', 'unrealisedPnl': '-6.1183', 'markPrice': '117920.7', 'adlRankIndicator': '2', 'cumRealisedPnl': '0.8029038', 'positionMM': '4.56943979', 'createdTime': '1753151354207', 'positionIdx': '0', 'positionIM': '83.56794379', 'seq': '140710307682980', 'updatedTime': '1753286400053', 'side': 'Buy', 'bustPrice': '', 'positionBalance': '0', 'leverageSysUpdatedTime': '', 'curRealisedPnl': '-0.6232491', 'size': '0.007', 'positionStatus': 'Normal', 'mmrSysUpdatedTime': '', 'stopLoss': '', 'tradeMode': '0', 'sessionAvgPrice': '', 'nextPageCursor': 'BTCUSDT%2C1753286400053%2C0'}, 'id': None, 'symbol': 'BTC/USDT:USDT', 'timestamp': 1753151354207, 'datetime': '2025-07-22T02:29:14.207Z', 'lastUpdateTimestamp': 1753286400053, 'initialMargin': 83.56794379, 'initialMarginPercentage': 0.10049500000721533, 'maintenanceMargin': 4.56943979, 'maintenanceMarginPercentage': 0.005495000007215326, 'entryPrice': 118794.74285714, 'notional': 831.5632, 'leverage': 10.0, 'unrealizedPnl': -6.1183, 'realizedPnl': None, 'contracts': 0.007, 'contractSize': 1.0, 'marginRatio': None, 'liquidationPrice': None, 'markPrice': 117920.7, 'lastPrice': None, 'collateral': 0.0, 'marginMode': None, 'side': 'long', 'percentage': None, 'stopLossPrice': None, 'takeProfitPrice': None, 'hedged': False}

    """
        #print(" ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; ")
        #pprint(self._exchange.parse_positions(linear_positions))

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

class yk_Bybit_demo(yk_Bybit):

    def __init__(self, exchange_name, cfg_Jdata ):

        super().__init__( exchange_name, cfg_Jdata )

        self._cl_name = self.__class__.__name__

    def setMarket(self, market='spot'):
        self._exchange.options['defaultType'] = market   #  swap   very important set swap as default type
        self._markets = self._exchange.load_markets(True)


    def connect(self, demo=True, market='swap'):
        self._exchange = ccxt.bybit(
            {'apiKey': self._apiKey, 'secret': self._apiSecret, 'verbose': True})

        self._exchange.options['defaultType'] = market  # spot, swap, features, option
        self._exchange.options["enableDemoTrading"] = True
        self._exchange.options['enableUnifiedMargin'] = True
        self._exchange.options['enableUnifiedAccount'] = True

        if demo :
            self._exchange.enable_demo_trading( demo )

        # move to sandbox
        # self._exchange.urls['api'] = self._exchange.urls['testDemo']
        #self._exchange.urls['api'] = self._exchange.urls['test']

        print( self._exchange.privateGetV5AccountInfo() )


        self._exchange.verbose = False
        secret = self._exchange.secret
        self._exchange.secret = None

        p = { "enableDemoTrading": True, 'verbose': False }
        markets = self._exchange.load_markets(params=p)  # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets

        self._exchange.secret = secret
        self._exchange.verbose = True


class BybitOrder( base_Order ):
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

    type = 'limit'
    side = 'sell'
    size = 0

    order_price = 0
    stop_loss = 0

    def get_order_type(self):
        if self.type == 'market':
            return 'Market'
        elif self.type == 'limit':
            return 'Limit'
        elif self.type == 'stop_loss':
            return 'StopLoss'
        elif self.type == 'take_profit':
            return 'TakeProfit'
        else:
            return self.type.capitalize()

    def __init__(self, monitor, sym, type='market', side='buy',
                 coin_amount=0, usd=0, leverage=50, price=0, stopPrice=0, tp=None, sl=None):

        super().__init__( monitor, sym, type, side, coin_amount, usd, leverage, price, stopPrice, tp, sl)

        self.pos_MaxLossProc = 40  # max loss % per pos;  40%;

        self.pos = None
        self.sl_id = None
        self.sl_order = "None"

        self.coin_price = self.get_coinPrice()
        self.set_leverage(self.leverage)

        #self.check_leverage_and_size(leverage, amount)

        self.monitor.logInfo(" tradePos: Order==========================:")
        self.monitor.logInfo(self.sym, self.type, self.side, f"size={self.size}")

    @classmethod
    def CreateMarketOrder(cls, monitor, sym, side='buy', coins = 0, usd=0, leverage=50):
        """
        Create a market order instance.
        :param monitor: Monitor instance for logging.
        :param sym: Symbol for the order.
        :param side: 'buy' or 'sell'.
        :param amount: Amount to trade.
        :param leverage: Leverage for the order.
        :return: bybitOrder instance.
        """
        tek = 12
        order_price = 12

        return cls(monitor, sym, 'market', side, coins, usd, leverage, 0, 0, None, None)

    @classmethod
    def CreateLimitOrder(cls, monitor, sym, side='buy', coins = 0, usd=0, leverage=50, price=0):
        """
        Create a market order instance.
        :param monitor: Monitor instance for logging.
        :param sym: Symbol for the order.
        :param side: 'buy' or 'sell'.
        :param amount: Amount to trade.
        :param leverage: Leverage for the order.
        :return: bybitOrder instance.
        """

        return cls(monitor, sym, 'limit', side, coins, usd, leverage, price, 0, None, None)

    @classmethod
    def CreateStopOrder(cls, monitor, sym, side='buy', coins = 0, usd=0, leverage=50, price=0):

        return cls(monitor, sym, 'limit', side, coins, usd, leverage, price, 0, None, None)

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

    def get_coinPrice(self):
        """
        Get the current price of the coin.
        :return: Current coin price.
        """
        return self.monitor.get_ticker_price( self.sym )

    def check_coinAmount(self):
        if self.coin_amount == 0:
            self.coin_amount = self.usd * self.leverage / self.get_coinPrice()  # number of coins


    def check_leverage_and_size(self, leverage, amount):
        self.set_leverage(leverage)

        self.usd = amount  # USDT
        self.check_position_size()

    def set_leverage(self, leverage=0):

        #s1 = self.sym.split('/')  # 'MANA/USDT:USDT'
        #s2 = s1[1].split(':')  # USDT:USDT
        #sym = s1[0] + s2[1]  # 'MANAUSDT'

        s1 = self.sym.split('/')  # 'MANA/USDT'
        sym = s1[0] + s1[1]  # 'MANAUSDT'

        rc = self.exc.fetch_leverage_tiers([sym], {'symbol': sym})
        lev = int( rc[self.symbol][0]['maxLeverage'])

        if leverage > 0: self.leverage = leverage
        if lev < self.leverage: self.leverage = lev

        if lev != self.leverage:
            try:
                rcl = self.exc.set_leverage(self.leverage, self.symbol)
            except Exception as e:
                self.monitor.logInfo("OpenPosition Exception: ", e)
                self.monitor.logException(e)
                # if 'retcode' == 110043 - leverage is not modify

        self.monitor.logInfo(f"tradePos: Leverage = {self.leverage} ")

    def check_position_size(self):

        # leverage = 1; price = 100 X/USDT; money = $100 USD; pos = 100 USDT ( 1 X/USDT )
        # price2 = 90 X/USDT; price change = -$10 = -10%  pos change = -$10; money loss = -$10 = 10%

        # leverage = 10; price = 100 X/USDT; money = $100 USD; pos = 1000 USDT   ( 10 * X/USDT )
        # price2 = 90 X/USDT; price change = -$10 = -10%  pos change = 10 * price change = -$100; money loss = 100%

        # price change = D%  pos change = ( D% * leverage )% = L%  money loss = L%

        self.size = self.usd * self.leverage / self.coin_price  # number of coins

        PriceChangeProc = (self.pos_MaxLossProc / self.leverage) / 100
        self.stop_loss = self.coin_price * (1 + (-PriceChangeProc if self.side == 'buy' else PriceChangeProc))


    def set_take_profit_and_stop_loss_params(self, symbol: str, type: OrderType, side: OrderSide,
        amount: float, price: Num = None, takeProfit: Num = None, stopLoss: Num = None, params={}):

        params = {
            #'takeProfit': takeProfit if takeProfit is not None else 0,
            #'stopLoss': stopLoss if stopLoss is not None else 0,
            'takeProfitAmount': 'last',  # 'last', 'mark' or 'index'
            'takeProfitType': 'limit',  # 'market' or 'limit'
            'takeProfitPriceType': 'last',  # 'last', 'mark' or 'index'
            'takeProfitLimitPrice': 'last',  # 'last', 'mark' or 'index'

            'stopLossAmount': 'limit',  # 'market' or 'limit'
            'stopLossType': 'limit',  # 'market' or 'limit'
            'stopLossPriceType': 'last',  # 'last', 'mark' or 'index'
            'stopLossLimitType': 'last',  # 'last', 'mark' or 'index'
            # additional params can be added here
        }

        self.params = self.exc.set_take_profit_and_stop_loss_params( symbol, type, side,
            amount, price, takeProfit, stopLoss, params={} )


    def add_TakeProfitData(self, amount, price, triggerPrice, type='market', priceType='mark'):

        self.params['takeProfit'] = {
                'amount': amount,
                'price': price,
                'triggerPrice': triggerPrice,
                'type': type,           # 'market' or 'limit'
                'priceType': priceType  # last | mark | index
            }

    def add_StopLossData(self, amount, price, triggerPrice, type='market', priceType='mark'):

        self.params['stopLoss'] =  {
            'amount': amount,
            'price': price,
            'triggerPrice': triggerPrice,
            'type': type,           # 'market' or 'limit'
            'priceType': priceType  # last | mark | index
        }

    def openOrder(self):

        print( f"--> openOrder: {self.symbol}, {self.type}, {self.side}, {self.coin_amount}" )
        self.info = self.exc.create_order( self.symbol, self.type, self.side, self.coin_amount, self.price, self.params )

        self.id= self.info['id']
        print( f'Create order {self.id = }' )
        return self.info

    def checkOrder(self):
        info = self.exc.fetch_order( self.info['id'], self.sym, {'acknowledged':True, 'type':'swap'} )
        pprint ( info )
        return info

    def openMaker_Market(self):
        """symbol = 'LTC/USDT:USDT'
        type = 'market'
        side = 'buy'
        amount = 0.1
        price = None"""

        self.type = 'market'
        self.check_coinAmount()

        self.price = None

        return self.openOrder()

    def openMaker_Limit(self, price = 0.):  # price < market price if buying
        """ symbol = 'LTC/USDT:USDT'
        type = 'limit'
        side = 'buy'
        amount = 0.1
        price = 200"""

        self.type = 'limit'

        self.check_coinAmount()

        if price > 0: self.price = price
        return self.openOrder()

    def openMaker_Stop(self, stopPrice=0. ):  # price > market if buying

        self.check_coinAmount()

        if stopPrice > 0: self.stopPrice = stopPrice

        self.type='market'
        self.params = {'triggerDirection': 'above' if self.side == 'buy' else 'below'}
        #self.params = {'triggerDirection': 'up' if self.side == 'sell' else 'down'}

        self.info = self.exc.create_stop_order( self.symbol, self.type, self.side,
                    self.coin_amount, None, self.stopPrice, params=self.params)

        print( f'Create order {self.info['id'] = }' )
        return self.info


    def openTaker_TakeProfit(self, coin_amount=0, tp_Price=0):
        side = 'sell' if self.side == 'buy' else 'buy'
        self.info = self.exc.create_take_profit_order( self.symbol, 'market', side,
                    coin_amount, None, tp_Price )
        return self.info


    def addTaker_TakeProfit(self, coin_amount=0, tp_Price=0):
        side = 'sell' if self.side == 'buy' else 'buy'
        p = {
            'tpSize': str( coin_amount),
            'tpslMode': 'Partial',
            'PositionTpSl': True
        }
        self.info = self.exc.create_take_profit_order( self.symbol, 'market', side,
                    coin_amount, None, tp_Price, p )
        return self.info

    def openTaker_Limit(self):
        pass

    def openTaker_StopLimit(self):
        pass

    #    def openPosition(self, tp=[0,0,0], tpd=[0,0,0], tpsize=[0,0,0], order_price=0, sl=[0,0] ):
    def openPositionX(self, tp=[0, 0, 0], tpsize=[0, 0, 0], sl=[0, 0]):
        # self.entry_price = order_price
        # self.order_price = order_price
        self.tp = tp
        self.tpsize = tpsize

        cur_price = order_price
        if self.type == 'market':
            tik = self.exc._exchange.fetch_ticker(self.sym)
            # self.order_price = int(tik['info']['markPrice'])
            cur_price = tik['last']

        if sl[0] > 0:
            self.stop_loss = sl[0]
        else:
            self.stop_loss = cur_price - sl[1] if self.side == 'buy' else cur_price + sl[1]

        for i in range(3):
            if self.tp[i] == 0:
                self.tp[i] = cur_price + tpd[i] if self.side == 'buy' else cur_price - tpd[i]

        p = {
            'tpslMode': 'Partial',
            'tpSize': str(tpsize[2]),
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
            self.sym, self.type, self.side, self.size, params=p)

        self.sl_id = ord['id']

        self.pos = self.monitor.FetchOpenPosition(self.sym)
        self.entry_price = self.pos['entryPrice']

        if self.entry_price is not None:
            self.changeSL(self.stop_loss)
            return True

        self.addTPLimit(self.tpsize[0], self.tp[0])
        self.addTPLimit(self.tpsize[1], self.tp[1])

        return False

    def openPosition(self, tp=[], sl=[0, 0]):

        len_tp = len(tp)
        if len_tp == 0 or len_tp > 4:
            self.monitor.logError("tradePos **************   size of TP is incorrect ")
            return None

        self.tp = tp
        self.sl = sl

        if self.sl[0] == 0:
            self.sl[0] = self.stop_loss

        # check tp sizes
        if len_tp == 1:
            self.tpsize = [self.size]

        elif len_tp == 2:
            self.tpsize = [self.size * 0.5, self.size * 0.5]

        elif len_tp == 3:
            self.tpsize = [self.size * 0.4, self.size * 0.4, self.size * 0.2]

        elif len_tp == 4:
            self.tpsize = [self.size * 0.3, self.size * 0.3, self.size * 0.2, self.size * 0.2]

        n = len_tp - 1
        p = {
            'tpslMode': 'Partial',
            'tpSize': str(self.tpsize[n]),
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
            self.monitor.logInfo("tradePos Order parameters ==========================:")
            self.monitor.logInfo(p)

            self.monitor.logInfo(" ===============:")
            self.monitor.logInfo("tradePos: Create Main Order ===============:")

            #ord = self.exc.create_order_with_take_profit_and_stop_loss(
            ord = self.exc.create_order(
                self.sym, self.type, self.side, self.size, params=p)

            self.monitor.logInfo(" ===============:")
            self.monitor.logInfo("tradePos: Fetch position ===============:")

            self.pos = self.exc.fetch_position(self.sym, {})

            self.entry_price = self.pos['entryPrice']
            self.monitor.logInfo(f"tradePos: Order Entry price: {self.entry_price}")

            self.monitor.logInfo("tradePos: Create TP/SL ===============:")

            for i in range(len_tp):
                if self.tp[i] > 0 and self.tpsize[0] > 0:
                    self.monitor.logInfo(f"tradePos: Create TP/SL ===============: {i}")
                    self.addTPLimit(self.tpsize[i], self.tp[i])

            self.monitor.logInfo(" ===============:")
            self.monitor.logInfo("tradePos: Fetch orders ===============:")

            self.orders = self.exc.fetch_open_orders(self.sym)

            for ord in self.orders:
                if 'StopLoss' in ord['info']['createType']:
                    self.sl_order = ord

        except Exception as e:
            self.monitor.logInfo("OpenPosition Exception: ", e)
            self.monitor.logException(e)

        return self.pos

    def readPosition(self):
        self.pos = self.exc.FetchOpenPosition(self.sym)
        self.entry_price = self.pos['entryPrice']
        if self.entry_price is not None:
            # self.type = self.pos['type']
            self.side = self.pos['info']['side'].lower()
            self.size = float(self.pos['info']['size'])
            self.order_price = self.entry_price

            return True
        return False

    def waitOpenPosition(self, timeout=1):
        while timeout > 0:
            self.pos = self.exc.FetchOpenPosition(self.sym)
            self.entry_price = self.pos['entryPrice']
            if self.entry_price is not None:
                return True
            time.sleep(1)
            timeout -= 1

        return False

    def addTPLimit(self, size, price):
        side = 'sell' if self.side == 'buy' else 'buy'
        p = {'tpSize': str(size), 'tpslMode': 'Partial', 'PositionTpSl': True}

        return self.exc.create_take_profit_order(self.sym, 'limit', side, size, price, takeProfitPrice=price, params=p)

    def addTP__(self, size, d_price, d_tr_price=1):
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
        self.exc.CreateTakeProfitandStopLoss2(self.sym, 'limit', side, size, tp_price, param=param)

    def EditLimitOrder(self, id, amount, price, tr_price):
        side = 'sell' if self.side == 'buy' else 'buy'
        return self.exc._exchange.edit_order(id, self.sym, 'limit', side, amount, price,
                                             params={'triggerPrice': tr_price})

    def editSL(self, price, amount=None):
        # dd = 'sell' if self.side == 'buy' else 'buy'
        amount = self.size if amount is None else amount
        return self.EditLimitOrder(self.sl_order['id'], amount, price, price)

    def str(self):
        if self.pos is not None:
            return ("\n ================================="
                    f" {self.sym} {self.type} {self.side} size={self.size} leverage= {self.leverage}\n"
                    f" entry_price={self.entry_price} order_price={self.order_price}\n"
                    f" takeProfit: {self.tp}  profitSize: {self.tpsize}\n"
                    f" stopLoss: {self.sl}\n"
                    f" SLOrder: {self.sl_order}\n"
                    "=================================\n"
                    )
        else:
            return "\n ********* Position is empty !  ************\n"

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


class trade(object):
    type = 'limit'
    side = 'sell'
    size = 0

    order_price = 0
    stop_loss = 0

    def __init__(self, exchange, sym, type=None, side=None, size=None):
        self.pos = {}
        self.sl_id = None

        self.exc = exchange
        self.sym = sym
        self.type = type
        self.side = side
        self.size = size

    def openPosition(self, order_price=0, d_stop_loss=0):
        self.entry_price = order_price
        self.order_price = order_price
        self.stop_loss = d_stop_loss

        if self.type == 'market':
            tik = self.exc._exchange.fetch_ticker(self.sym)
            # self.order_price = int(tik['info']['markPrice'])
            self.order_price = tik['last']

        self.stop_loss = self.order_price - d_stop_loss if self.side == 'buy' else self.order_price + d_stop_loss

        ord = self.exc._exchange.create_order_with_take_profit_and_stop_loss(self.sym, self.type, self.side, self.size,
                                                                             self.order_price, None, self.stop_loss,
                                                                             {'tpslMode': 'partial'})

        self.sl_id = ord['id']

        self.pos = self.exc.FetchOpenPosition(self.sym)
        self.entry_price = self.pos['entryPrice']
        if self.entry_price is not None:
            self.changeSL(d_stop_loss)

            return True
        return False

    def readPosition(self):
        self.pos = self.exc.FetchOpenPosition(self.sym)
        self.entry_price = self.pos['entryPrice']
        if self.entry_price is not None:
            # self.type = self.pos['type']
            self.side = self.pos['info']['side'].lower()
            self.size = float(self.pos['info']['size'])
            self.order_price = self.entry_price

            return True
        return False

    def waitOpenPosition(self, timeout=1):
        while timeout > 0:
            self.pos = self.exc.FetchOpenPosition(self.sym)
            self.entry_price = self.pos['entryPrice']
            if self.entry_price is not None:
                return True
            time.sleep(1)
            timeout -= 1

        return False

    def addTP(self, size, d_price, d_tr_price=1):
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
        self.exc.CreateTakeProfitandStopLoss2(self.sym, 'limit', side, size, tp_price, param=param)

    def changeSL(self, d_price):

        orders = self.exc.FetchOpenOrders(self.sym)
        for ord in orders:
            if ord['stopLossPrice'] is not None:
                self.stop_loss = self.entry_price + d_price if ord[
                                                                   'side'].lower() == 'buy' else self.entry_price - d_price
                self.exc.EditOrder2(ord['id'], self.sym, ord['type'], ord['side'], ord['amount'],
                                    param={'stopLossPrice': self.stop_loss})
                return True
        """            
            self.stop_loss  = self.order_price - d_stop_loss if self.side == 'buy' else self.order_price + d_stop_loss
            # side for stopLoss order is invers to open order
            side = 'buy' if self.side == 'sell' else 'sell'
            self.exc.EditOrder2( self.sl_id, self.sym, 'market', side, self.size, param={'stopLossPrice': self.stop_loss} )
        """
        return False

    def print(self):
        print(f" Open:  {self.type}  {self.side}  {self.size} ")
        print(f" Open:  {self.order_price}  {self.entry_price}  stopLoss: {self.size}  {self.stop_loss}")