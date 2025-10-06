# -*- coding: utf-8 -*-

import ccxt as ccxt  # noqa: E402
from ccxt.base.types import (Balances, Currency, Greeks,
     Int, Leverage, Market, MarketInterface, Num,
     Option, OptionChain,
     Order, OrderBook, OrderRequest, OrderSide, OrderType, Str,
    Strings, Ticker, Tickers, Trade, Transaction, TransferEntry)

from typing import List
from pprint import pprint


import tools as T
from base_exchange import base_Exchange, Position

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



