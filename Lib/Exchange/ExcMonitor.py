
import asyncio, time

if __name__ == '__main__':
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config as acfg

import tools as T, gMessage as M, utils as U
from colorPrint import colorPrint as clp

from yk_bybit import yk_Bybit_demo
#from bybit_exchange_pro import bybit_Exchange_pro

from positions import BybitPosition, orderSide, orderType, orderState, orderData


class TExchange(yk_Bybit_demo):

    def __init__(self, p, cfg_data ):

        super().__init__( p["exc_keys"], cfg_data)

        queues = p['queues']

        if queues is not None:
            self.q_toMainMonitor   = queues[0]  # put a ctrl msg
            self.q_fromMainMonitor = queues[1]  # get a ctrl msg
            self.q_fromTMonitor    = queues[2]  # get a data from another worker thread ( TMonitor )
        else:
            self.q_toMainMonitor   = M.xQueue()  # put a ctrl msg
            self.q_fromMainMonitor = M.xQueue()  # get a ctrl msg
            self.q_fromTMonitor    = M.xQueue()  # get a data from another worker thread ( Exchange )

        self.q_handler = M.xQueue() # get data from msg handlers

        self.msg_toMainMonitor = M.CtrlMsg('TExchange', 'MainMonitor')
        #self.msgO = M.CtrlMsg('TExchange', 'Thread-2')

        # position processing for channel:
        self.chan_call = {
            'YK-Test': self.openPosition_Test,
            'Мастерство трейдинга': self.openPosition,
            'Crypto Daniel': self.openPosition,
            'Trade Indicator 🚀': self.openPosition,
            'Криптонец': self.openPosition,

            'Cornix Notifications': self.openPosition_Cornix
        }

    async def Start(self, tout = 0 ):

        def test():
            sym = "BTC/USDT:USDT"
            self.print_red(" after open")

            pos = BybitPosition(self, sym)

            if pos.readPosition():
                # pos.addTP(0.03, 100)
                # print( bybit.FetchOpenOrders(sym))
                pos.changeSL(100)

        self.logInfo(" EMonitor: Starting....", cs=clp.yellow )
        #bybit = openBybit(path, cfg_file, section, exc_keys)
        self.connect(market='swap')

        # test(); return

        self.msg_toMainMonitor.body = "EMonitor initiated"
        self.logInfo( self.msg_toMainMonitor.date(), cs=clp.yellow )
        #self.q_ctrl_out.async_put_nowait(copy.deepcopy(msgX))
        self.q_toMainMonitor.async_put_nowait( self.msg_toMainMonitor )

        self.logInfo("EMonitor is started", cs=clp.yellow)

        # main loop
        start = time.perf_counter()

        await self.main_loop( tout )

        # exit from Run
        duration = time.perf_counter() - start

        self.logInfo(" EMonitor Stopped", cs=clp.yellow)

        self.msg_toMainMonitor.status = 'Exit'
        k = 1
        self.msg_toMainMonitor.body = f'Exchange Monitor exit after {k} sec'
        self.q_toMainMonitor.async_put_nowait(self.msg_toMainMonitor.date())

        return

    async def main_loop(self, tout):
        if tout > 0:
            check_timer = asyncio.create_task(U.task_timer( tout, 3600 ))

        is_running = True
        start = time.perf_counter()
        k = 0

        while is_running and ( True if tout == 0 else check_timer.done() == False ):
            try:
                if k % 300 == 0:
                    self.logInfo( f"Exchange monitor is working.... {k} sec", cl='green' )
                    #self.msgC.body = f'==> to Main TMonitor are working.... {k} sec'
                    #self.q_ctrl_out.async_put_nowait( copy.deepcopy(self.msgC.date()) )
                    #print(T.blue("Msg to Main sent"))

                    #self.msgO.body = f'==> to Thread2 ====> TMonitor running {k} sec'
                    #self.q_out.async_put_nowait(self.msgO.date())
                    #print(T.blue("Msg to Thread2 sent"))

                # check ctrl queue from mainThread
                await self.check_mainMonitor_queue()

                # check data queue from TMonitor
                await self.check_TMonitor_queue()

                #check opened positions

            except Exception as e:
                self.logInfo("MainLoop Exception: ", e)
                self.logException(e)

            await asyncio.sleep(1)
            k += 1

    async def check_mainMonitor_queue(self):

        while not self.q_fromMainMonitor.empty():
            msgQ = await self.q_fromMainMonitor.async_get()
            self.logInfo("EMonitor read MainMonitor queue: ", msgQ, cs=clp.green)
            self.q_fromMainMonitor.task_done()

            if msgQ.status == 'Exit':
                is_running = False

    async def check_TMonitor_queue(self):

        while not self.q_fromTMonitor.empty():
            qMsg = await self.q_fromTMonitor.async_get()  # class CtrlMsg
            self.logInfo("EMonitor read TMonitor queue:\n", qMsg, cs=clp.green)
            self.q_fromTMonitor.task_done()

            if qMsg.status == 'Order':
                if self.create_new_position( qMsg ) is not None:
                    self.msgC.body = "new position was created"
                else:
                    self.msgC.body = "new position was not created"

                # notify mainThread
                self.q_toMainMonitor.async_put_nowait(self.msgC.date())
                self.print_green("Msg to mainThread sent")

    def create_new_position(self, qmsg ):

        order_msg = qmsg.body   #  TMessage.Order_Info class

        sym = order_msg.symbol  # BTC/USDT
        # do we have opened position for this symbol ?
        #
        if self.FetchOpenPosition( sym ) is not None:
            self.logInfo( f"Position for {sym} already exists. New position will not be created", cs=clp.red )
            return None

        leverage = order_msg.leverage # 30
        np =BybitPosition( self, sym, leverage )

        if order_msg.base_size > 0:
            usdt = order_msg.base_size
            coins = None
        else:
            usdt = None
            coins = order_msg.coin_size

        if usdt is None and coins is None:
            self.logInfo( f"Position for {sym} has no size. New position will not be created", cs=clp.red )
            return None

        np.set_Main_order(order_msg.order_type, order_msg.order_act, usdt=usdt, coins = coins)

        np.add_StopLoss_order( orderType.Market, sl_price= order_msg.slPrice[0] )
        l = len( order_msg.tpPrice )
        np.add_TakeProfit_order( 1, orderType.Market, tp_price= order_msg.tpPrice[ l-1 ] )

        #pprint( np )
        np.open()

        for tp in order_msg.tpPrice[1:]:
            if tp[0] > 0:
                #np.open_TakeProfit_Part( usdt=tp[1], tp_price= tp[0] )
                pass

        self.logInfo(f"New position for {sym} is created", cs=clp.yellow)

        # check position
        # add to dictionary
        # save dictionary to file
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


    def openPosition_Test(self, qMsg):

        pMsg = qMsg.body  # parserMsg

        sym = pMsg.symbol + ":USDT" #BTC/USDT:USDT"
        side = pMsg.getDirection()  #'buy'
        size = pMsg.size

        pos = BybitPosition(self, sym, side=side, size=size)
        tp = [0, 0, 0]
        tps = [0.04, 0.04, 0.02]
        sl = [0, 0]

        c_price = self._exchange.fetch_ticker(sym)['last']

        if side == 'buy':
            tp[0] = c_price + 300
            tp[1] = c_price + 400
            tp[2] = c_price + 500
            sl[0] = c_price - 500
        else:
            tp[0] = c_price - 300
            tp[1] = c_price - 400
            tp[2] = c_price - 500
            sl[0] = c_price + 500

        pos.openPosition(tp, tps, sl)
        # print( bybit._exchange.fetch_my_trades( sym ) )
        return pos

#=============================================
    def openPosition(self, qMsg):
        # master trading
        pMsg = qMsg.body  # parserMsg
        pos = BybitPosition(self, pMsg.symbol, side=pMsg.getDirection(), size=pMsg.size, leverage=pMsg.leverage)
        rc = pos.openPosition( pMsg.tpPrice, pMsg.slPrice)

        self.logInfo( "Open position: ", pos.str() if rc else "Position was not open")

        # print( bybit._exchange.fetch_my_trades( sym ) )
        return pos

    def openPosition_Cornix(self, qMsg):
        # master trading
        pMsg = qMsg.body  # parserMsg

        usd = 30        # max usd per trade: 10% from $300
        leverage = 50 if pMsg.leverage == 0 else pMsg.leverage

        # price1 = 50000; price2 = 50050; change = 0.1%  pos change = 0.1 * leverage ( 10% )
        # max pos loss <= 40%  => max price change= 0.4/leverage
        # price change = (pos change)%/leverage
        maxPosLoss = 0.4     # max pos loss % per trade; 40%;  price change= 0.4/leverage
        maxPriceChange = maxPosLoss/leverage

        sym = pMsg.symbol + ":USDT" #BTC/USDT:USDT"
        side = pMsg.getDirection()  #'buy'

        size = pMsg.size
        sl = pMsg.slPrice

        if size == 0 or sl[0] == 0:
            c_price = self._exchange.fetch_ticker(sym)['last']
            if size == 0:
                size = usd * leverage / c_price # number of coins

            if sl[0] == 0:
                sl[0] = c_price * ( 1 - maxPriceChange ) if side == 'buy' else c_price * ( 1 + maxPriceChange )

        pos = BybitPosition(self, sym, side=side, size=size, leverage=leverage)
        tp = pMsg.tpPrice

        tps = [ size*0.4, size*0.4, size*0.2]

        pos.openPosition(tp, tps, sl)

        self.logInfo( pos.str() )

        # print( bybit._exchange.fetch_my_trades( sym ) )
        return pos

# this is main entry point
async def start_Exchange( p ):

    # 1. read cfg file:
    cfg_data = T.CfgJson( cfg_mem=p['cfg_mem'], prefix="EMonitor" )
    cfg_data.openLog( lname='Emonitor')

    # 2. Init Exchange:
    bybit = TExchange( p, cfg_data )
    await bybit.Start()

#==================================
async def test_Exchange():
    cq_get = M.xQueue()     # mainThread will get
    cq_put = M.xQueue()     # mainThread will put
    dq12_put = M.xQueue()   # Tmonitor will put data for  exchange thread
    dq12_get = M.xQueue()   # Tmonitor will get data from exchange thread

    cfg_data = T.CfgJson(acfg.cfg_files + "\\cfg-Emonitor.json")

    param = {
        "cfg_mem"  : cfg_data.cfg_all,
        #"section"  : "EMonitor",
        "exc_keys" : acfg.bybit_key_demo,
        "queues"   : [cq_get, cq_put, dq12_put, dq12_get]
    }

    await start_Exchange( param )


if __name__ == '__main__':
    asyncio.run( test_Exchange() )


async def start_Exchange_2( p ):
    await asyncio.sleep(300)

async def test_Exchange_2(path, cfg_file, section, exc_keys, queue):
    # 1. read cfg file:
    path = "/Files\\"
    jdata = T.CfgJson(cfg_file=path + "cfg-h1.json", section="ChannelH1")  # ,cfg=None )

    # 2. Init Exchange:
    bybit = yk_Bybit_demo('ByBitDemoAll', jdata)

    #bybit.connect()
    bybit.connect( market='swap' )
    return bybit


"""
fetchTicker()    
{'symbol': 'BTC/USDT:USDT', 'timestamp': None, 'datetime': None,
 'high': 65700.0, 'low': 64026.6, 'bid': 64804.4, 'bidVolume': 0.347, 'ask': 64804.5, 'askVolume': 12.494, 
 'vwap': 65054.12724473863, 
 'open': 64479.0, 'close': 64804.5, 
        'last': 64804.5, 
 'previousClose': None, 'change': 325.5, 'percentage': 0.5048, 
 'average': 64641.75, 'baseVolume': 82717.325, 'quoteVolume': 5381103385.8944, 
 'info': {'symbol': 'BTCUSDT', 
          'lastPrice': '64804.50',
           'indexPrice': '64833.12', 
           'markPrice': '64815.40', 
          'prevPrice24h': '64479.00', 'price24hPcnt': '0.005048', 'highPrice24h': '65700.00', 'lowPrice24h': '64026.60', 
          'prevPrice1h': '65054.00', 'openInterest': '65463.693', 'openInterestValue': '4243055447.27', 
          'turnover24h': '5381103385.8944', 'volume24h': '82717.3250', 'fundingRate': '0.000058', 
          'nextFundingTime': '1718841600000', 'predictedDeliveryPrice': '', 'basisRate': '', 'deliveryFeeRate': '', 'deliveryTime': '0', 
          'ask1Size': '12.494', 'bid1Price': '64804.40', 'ask1Price': '64804.50', 'bid1Size': '0.347', 'basis': ''}
 }
 
 
 createMarket()
 {'info': 
    {'orderId': 'd6d09e63-122e-445f-b43d-216e2f64166b', 'orderLinkId': ''}, 
 'id': 'd6d09e63-122e-445f-b43d-216e2f64166b', 'clientOrderId': None, 'timestamp': None, 'datetime': None, 
 'lastTradeTimestamp': None, 'lastUpdateTimestamp': None, 'symbol': 'BTC/USDT:USDT', 'type': None, 
 'timeInForce': None, 'postOnly': None, 'reduceOnly': None, 'side': None, 
 'price': None, 'stopPrice': None, 'triggerPrice': None, 'takeProfitPrice': None, 'stopLossPrice': None, 
 'amount': None, 'cost': None, 'average': None, 'filled': None, 'remaining': None, 'status': None, 'fee': None, 'trades': [], 'fees': []
 }
 
 
 
 fetchPosition() // no open positions
 rc= {'info': 
 {'symbol': 'BTCUSDT', 'leverage': '10', 'autoAddMargin': '0', 'avgPrice': '0', 'liqPrice': '', 'riskLimitValue': '2000000', 
 'takeProfit': '', 'positionValue': '', 'isReduceOnly': False, 'tpslMode': 'Full', 'riskId': '1', 'trailingStop': '0', 
 'unrealisedPnl': '', 'markPrice': '64841.6', 'adlRankIndicator': '0', 'cumRealisedPnl': '-3501.65243677', 
 'positionMM': '0', 'createdTime': '1717821325356', 'positionIdx': '0', 'positionIM': '0', 'seq': '478604949', 
 'updatedTime': '1718763448079', 
 'side': '', 'bustPrice': '', 'positionBalance': '0', 'leverageSysUpdatedTime': '', 'curRealisedPnl': '0', 'size': '0', 
 'positionStatus': 'Normal', 'mmrSysUpdatedTime': '', 'stopLoss': '', 
 'tradeMode': '0', 'sessionAvgPrice': ''
 }, 
 'id': None, 'symbol': 'BTC/USDT:USDT', 'timestamp': 1718827044381, 
 'datetime': '2024-06-19T19:57:24.381Z', 'lastUpdateTimestamp': None, 
 'initialMargin': 0.0, 'initialMarginPercentage': None, 
 'maintenanceMargin': 0.0, 'maintenanceMarginPercentage': None, 
    'entryPrice': None,
 'notional': None, 'leverage': 10.0, 
 'unrealizedPnl': None, 'contracts': 0.0, 'contractSize': 1.0, 
 'marginRatio': None, 'liquidationPrice': None, 'markPrice': 64841.6, 'lastPrice': None, 
 'collateral': 0.0, 
 'marginMode': None, 
 'side': None, 
 'percentage': None, 
 'stopLossPrice': None, 
 'takeProfitPrice': None
 }
 
 fetchPosition() // open positions
 {'info': 
 {'symbol': 'BTCUSDT', 'leverage': '10', 'autoAddMargin': '0', 'avgPrice': '64800.4', 'liqPrice': '', 
 'riskLimitValue': '2000000', 'takeProfit': '', 'positionValue': '6480.04', 'isReduceOnly': False, 'tpslMode': 'Full', 'riskId': '1', 
 'trailingStop': '0', 'unrealisedPnl': '-2.057', 
 'markPrice': '64779.83',
  'adlRankIndicator': '2', 'cumRealisedPnl': '-3505.21645877', 
 'positionMM': '35.6078198', 'createdTime': '1717821325356', 
 'positionIdx': '0', 'positionIM': '651.2116198', 'seq': '479992568', 'updatedTime': '1718829476354', 
 'side': 'Buy', 'bustPrice': '', 'positionBalance': '0', 'leverageSysUpdatedTime': '', 
 'curRealisedPnl': '-3.564022', 
 'size': '0.1', 
 'positionStatus': 'Normal', 
 'mmrSysUpdatedTime': '', 'stopLoss': '', 'tradeMode': '0', 'sessionAvgPrice': ''
 },
 'id': None, 'symbol': 'BTC/USDT:USDT', 'timestamp': 1718829734660, 'datetime': '2024-06-19T20:42:14.660Z', 'lastUpdateTimestamp': None, 
 'initialMargin': 651.2116198, 'initialMarginPercentage': 0.100495, 
 'maintenanceMargin': 35.6078198, 'maintenanceMarginPercentage': 0.005495, 
 'entryPrice': 64800.4, 
 'notional': 6480.04, 'leverage': 10.0, 'unrealizedPnl': -2.057, 'contracts': 0.1, 'contractSize': 1.0, 
 'marginRatio': None, 'liquidationPrice': None, 'markPrice': 64779.83, 'lastPrice': None, 'collateral': 0.0, 'marginMode': None, 
 'side': 'long', 'percentage': None, 'stopLossPrice': None, 'takeProfitPrice': None}
 
 
 fetchOpenOrders(sym1)
 [
 {'info': 
    {'symbol': 'BTCUSDT', 'orderType': 'Market', 'orderLinkId': '', 'slLimitPrice': '0', 
    'orderId': '18e562d0-3546-4fe8-8444-42be66a657c8', 'cancelType': 'UNKNOWN', 'avgPrice': '', 
    'stopOrderType': 'PartialStopLoss', 'lastPriceOnCreated': '64907.2', 
    'orderStatus': 'Untriggered', 'createType': 'CreateByPartialStopLoss', 
    'takeProfit': '', 'cumExecValue': '0', 
    'tpslMode': 'Partial', 'smpType': 'None', 'triggerDirection': '2', 'blockTradeId': '', 'isLeverage': '', 'rejectReason': 'EC_NoError', 
    'price': '0', 'orderIv': '', 'createdTime': '1718839000876', 'tpTriggerBy': '', 'positionIdx': '0', 'timeInForce': 'IOC', 
    'leavesValue': '0', 'updatedTime': '1718839000876', 
    'side': 'Sell', 'smpGroup': '0', 
    'triggerPrice': '64757.2', 'tpLimitPrice': '0', 'cumExecFee': '0', 'leavesQty': '0.1', 'slTriggerBy': '', 
    'closeOnTrigger': True, 'placeType': '', 'cumExecQty': '0', 'reduceOnly': True, 
    'qty': '0.1', 'stopLoss': '', 'marketUnit': '', 'smpOrderId': '', 'triggerBy': 'LastPrice'
    }, 
'id': '18e562d0-3546-4fe8-8444-42be66a657c8', 
'clientOrderId': None, 'timestamp': 1718839000876, 'datetime': '2024-06-19T23:16:40.876Z', 
'lastTradeTimestamp': 1718839000876, 'lastUpdateTimestamp': 1718839000876, 
'symbol': 'BTC/USDT:USDT', 
'type': 'market', 'timeInForce': 'IOC', 'postOnly': False, 'reduceOnly': True, 
'side': 'sell', 'price': None, 'stopPrice': 64757.2, 'triggerPrice': 64757.2, 
'takeProfitPrice': None, 
'stopLossPrice': 64757.2, 'amount': 0.1, 
'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.1, 'status': 'open', 
'fee': {'cost': '0', 'currency': 'USDT'}, 'trades': [], 'fees': [{'cost': 0.0, 'currency': 'USDT'}]
},
   
  {'info': 
    {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'orderLinkId': '', 'slLimitPrice': '0', 
    'orderId': 'bad3b72c-f82f-43ea-a366-a9d25ae0d85f', 'cancelType': 'UNKNOWN', 'avgPrice': '', 
    'stopOrderType': 'PartialTakeProfit', 'lastPriceOnCreated': '64907.2', 
    'orderStatus': 'Untriggered','createType': 'CreateByPartialTakeProfit', 
    'takeProfit': '', 'cumExecValue': '0', 
    'tpslMode': 'Partial', 'smpType': 'None', 'triggerDirection': '1', 'blockTradeId': '', 'isLeverage': '', 'rejectReason': 'EC_NoError', 
    'price': '65007.2', 'orderIv': '', 'createdTime': '1718839002579', 'tpTriggerBy': '', 'positionIdx': '0', 'timeInForce': 'GTC', 
    'leavesValue': '1950.216', 'updatedTime': '1718839002579', 
    'side': 'Sell', 'smpGroup': '0', 
    'triggerPrice': '65006.2', 'tpLimitPrice': '0', 'cumExecFee': '0', 'leavesQty': '0.03', 'slTriggerBy': '', 
    'closeOnTrigger': True, 'placeType': '', 'cumExecQty': '0', 'reduceOnly': True, 
    'qty': '0.03', 'stopLoss': '', 'marketUnit': '', 'smpOrderId': '', 'triggerBy': 'LastPrice'
    }, 
    'id': 'bad3b72c-f82f-43ea-a366-a9d25ae0d85f', 
    'clientOrderId': None, 'timestamp': 1718839002579, 'datetime': '2024-06-19T23:16:42.579Z', 
    'lastTradeTimestamp': 1718839002579, 'lastUpdateTimestamp': 1718839002579, 
    'symbol': 'BTC/USDT:USDT', 'type': 'limit', 'timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': True, 
    'side': 'sell', 'price': 65007.2, 'stopPrice': 65006.2, 'triggerPrice': 65006.2, 
    'takeProfitPrice': 65006.2, 
    'stopLossPrice': None, 'amount': 0.03, 
    'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.03, 'status': 'open', 
    'fee': {'cost': '0', 'currency': 'USDT'}, 'trades': [], 'fees': [{'cost': 0.0, 'currency': 'USDT'}]
   },
     
    {'info': 
        {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'orderLinkId': '', 'slLimitPrice': '0', 
        'orderId': 'd98a6375-d2b6-409c-bc5c-a2d833a766b4', 'cancelType': 'UNKNOWN', 'avgPrice': '', 
        'stopOrderType': 'PartialTakeProfit', 'lastPriceOnCreated': '64907.2', 'orderStatus': 'Untriggered', 
        'createType': 'CreateByPartialTakeProfit', 'takeProfit': '', 'cumExecValue': '0', 'tpslMode': 'Partial', 
        'smpType': 'None', 'triggerDirection': '1', 'blockTradeId': '', 'isLeverage': '', 'rejectReason': 'EC_NoError', 
        'price': '65057.2', 'orderIv': '', 'createdTime': '1718839003515', 'tpTriggerBy': '', 
        'positionIdx': '0', 'timeInForce': 'GTC', 'leavesValue': '2602.288', 'updatedTime': '1718839003515', 
        'side': 'Sell', 'smpGroup': '0', 'triggerPrice': '65056.2', 'tpLimitPrice': '0', 
        'cumExecFee': '0', 'leavesQty': '0.04', 'slTriggerBy': '', 'closeOnTrigger': True, 'placeType': '', 'cumExecQty': '0', 
        'reduceOnly': True, 
        'qty': '0.04', 'stopLoss': '', 'marketUnit': '', 'smpOrderId': '', 'triggerBy': 'LastPrice'
        }, 
        'id': 'd98a6375-d2b6-409c-bc5c-a2d833a766b4', 'clientOrderId': None, 
        'timestamp': 1718839003515, 'datetime': '2024-06-19T23:16:43.515Z', 
        'lastTradeTimestamp': 1718839003515, 'lastUpdateTimestamp': 1718839003515, 
        'symbol': 'BTC/USDT:USDT', 'type': 'limit', 'timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': True, 
        'side': 'sell', 'price': 65057.2, 'stopPrice': 65056.2, 'triggerPrice': 65056.2, 'takeProfitPrice': 65056.2, 
        'stopLossPrice': None, 'amount': 0.04, 'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.04, 
        'status': 'open', 'fee': {'cost': '0', 'currency': 'USDT'}, 'trades': [], 'fees': [{'cost': 0.0, 'currency': 'USDT'}]
    },
         
     {'info': 
        {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'orderLinkId': '', 'slLimitPrice': '0', 
        'orderId': 'e37b8a9d-e1d3-4da5-a90e-027133240dbd', 'cancelType': 'UNKNOWN', 'avgPrice': '', 
        'stopOrderType': 'PartialTakeProfit', 'lastPriceOnCreated': '64954.9', 'orderStatus': 'Untriggered', 
        'createType': 'CreateByPartialTakeProfit', 'takeProfit': '', 
        'cumExecValue': '0', 'tpslMode': 'Partial', 'smpType': 'None', 'triggerDirection': '1', 'blockTradeId': '', 
        'isLeverage': '', 'rejectReason': 'EC_NoError', 
        'price': '65007.2', 'orderIv': '', 'createdTime': '1718841497841', 'tpTriggerBy': '', 
        'positionIdx': '0', 'timeInForce': 'GTC', 'leavesValue': '1950.216', 'updatedTime': '1718841497841', 
        'side': 'Sell', 'smpGroup': '0', 'triggerPrice': '65006.2', 'tpLimitPrice': '0', 
        'cumExecFee': '0', 'leavesQty': '0.03', 'slTriggerBy': '', 'closeOnTrigger': True, 'placeType': '', 
        'cumExecQty': '0', 'reduceOnly': True, 'qty': '0.03', 'stopLoss': '', 'marketUnit': '', 'smpOrderId': '', 'triggerBy': 'LastPrice', 
        'nextPageCursor': 'e37b8a9d-e1d3-4da5-a90e-027133240dbd%3A1718841497841%2C18e562d0-3546-4fe8-8444-42be66a657c8%3A1718839000876'
        }, 
        'id': 'e37b8a9d-e1d3-4da5-a90e-027133240dbd', 
        'clientOrderId': None, 'timestamp': 1718841497841, 'datetime': '2024-06-19T23:58:17.841Z', 
        'lastTradeTimestamp': 1718841497841, 'lastUpdateTimestamp': 1718841497841, 
        'symbol': 'BTC/USDT:USDT', 'type': 'limit', 'timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': True, 
        'side': 'sell', 'price': 65007.2, 'stopPrice': 65006.2, 'triggerPrice': 65006.2, 'takeProfitPrice': 65006.2, 
        'stopLossPrice': None, 'amount': 0.03, 
        'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.03, 'status': 'open', 
        'fee': {'cost': '0', 'currency': 'USDT'}, 'trades': [], 'fees': [{'cost': 0.0, 'currency': 'USDT'}]
      }
      ]




 fetch_order_trades
 [
 {'id': 'd8c01241-1fc4-46cd-aef8-996ee0252296', 
 'info': {
 'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '57841bcc-3dd3-49e3-bcf9-08b8977e3485', 
 'stopOrderType': 'UNKNOWN', 'execTime': '1718395786421', 'feeCurrency': '', 'createType': 'CreateByUser', 
 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65520.94', 'execPrice': '65520.9', 'markIv': '', 
 'orderQty': '0.01', 'orderPrice': '65330', 'execValue': '655.209', 'closedSize': '0.01', 
 'execType': 'Trade', 'seq': '470893124', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 
 'isMaker': False, 'execFee': '0.36036495', 
 'execId': 'd8c01241-1fc4-46cd-aef8-996ee0252296', 'marketUnit': '', 'execQty': '0.01'
 }, 
 'timestamp': 1718395786421, 'datetime': '2024-06-14T20:09:46.421Z', 
 'symbol': 'BTC/USDT:USDT', 
 'order': '57841bcc-3dd3-49e3-bcf9-08b8977e3485', 
 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65520.9, 'amount': 0.01, 
 'cost': 655.209, 'fee': {'cost': 0.36036495, 'currency': 'USDT', 'rate': 0.00055}, 
 'fees': [{'cost': 0.36036495, 'currency': 'USDT', 'rate': 0.00055}]
 }, 
 
 {'id': 'b3cf5cdc-4a83-4712-ba87-e4a00a865b6e', 
 'info': {
 'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '7ba58443-e2c0-4c92-bf18-f8d64b3ffb64', 
 'stopOrderType': 'UNKNOWN', 'execTime': '1718395848987', 'feeCurrency': '', 'createType': 'CreateByUser', 
 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65510.55', 'execPrice': '65508', 'markIv': '', 
 'orderQty': '0.01', 'orderPrice': '65330', 'execValue': '655.08', 'closedSize': '0.01', 
 'execType': 'Trade', 'seq': '470894405', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 
 'isMaker': False, 'execFee': '0.360294', 
 'execId': 'b3cf5cdc-4a83-4712-ba87-e4a00a865b6e', 'marketUnit': '', 'execQty': '0.01'
 }, 
 'timestamp': 1718395848987, 'datetime': '2024-06-14T20:10:48.987Z', 
 'symbol': 'BTC/USDT:USDT', 
 'order': '7ba58443-e2c0-4c92-bf18-f8d64b3ffb64', 
 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65508.0, 'amount': 0.01, 
 'cost': 655.08, 'fee': {'cost': 0.360294, 'currency': 'USDT', 'rate': 0.00055}, 
 'fees': [{'cost': 0.360294, 'currency': 'USDT', 'rate': 0.00055}]
 }, 
 
 {'id': '473a439a-8ce7-4089-b60e-cd8cb414b5c1', 
 'info': {
 'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'eb9f8201-af35-49d8-902b-e7b190e44c57', 
 'stopOrderType': 'UNKNOWN', 'execTime': '1718396307929', 'feeCurrency': '', 'createType': 'CreateByUser', 
 'feeRate': '0.0002', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65635.2', 'execPrice': '65642.5', 'markIv': '', 
 'orderQty': '0.01', 'orderPrice': '65642.5', 'execValue': '656.425', 'closedSize': '0.01', 
 'execType': 'Trade', 'seq': '470904264', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 
 'isMaker': True, 'execFee': '0.131285', 
 'execId': '473a439a-8ce7-4089-b60e-cd8cb414b5c1', 'marketUnit': '', 'execQty': '0.01'
 }, 
 'timestamp': 1718396307929, 'datetime': '2024-06-14T20:18:27.929Z', 
 'symbol': 'BTC/USDT:USDT', 
 'order': 'eb9f8201-af35-49d8-902b-e7b190e44c57', 
 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'maker', 'price': 65642.5, 'amount': 0.01, 'cost': 656.425, 
 'fee': {'cost': 0.131285, 'currency': 'USDT', 'rate': 0.0002}, 'fees': [{'cost': 0.131285, 'currency': 'USDT', 'rate': 0.0002}]
 }, 
 
 {'id': '83aa2154-b06a-486f-9903-9fccabf6be28', 
 'info': {
 'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 
 'orderId': '4c74afaf-7732-4773-9957-a3ea03b1ed60', 
 'stopOrderType': 'Stop', 'execTime': '1718396879139', 'feeCurrency': '', 'createType': 'CreateByStopOrder', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65746.9', 'execPrice': '65800', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '62509.4', 'execValue': '658', 'closedSize': '0.01', 'execType': 'Trade', 'seq': '470916045', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.3619', 'execId': '83aa2154-b06a-486f-9903-9fccabf6be28', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718396879139, 'datetime': '2024-06-14T20:27:59.139Z', 'symbol': 'BTC/USDT:USDT', 'order': '4c74afaf-7732-4773-9957-a3ea03b1ed60', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65800.0, 'amount': 0.01, 'cost': 658.0, 'fee': {'cost': 0.3619, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.3619, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'd5e0c77f-b2b0-4bcd-9b3a-ea87852b2858', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '5f5dee34-2af6-4835-88ed-29690b16352a', 'stopOrderType': 'UNKNOWN', 'execTime': '1718398423570', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65658', 'execPrice': '65658', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '62375.1', 'execValue': '656.58', 'closedSize': '0', 'execType': 'Trade', 'seq': '470947597', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.361119', 'execId': 'd5e0c77f-b2b0-4bcd-9b3a-ea87852b2858', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718398423570, 'datetime': '2024-06-14T20:53:43.570Z', 'symbol': 'BTC/USDT:USDT', 'order': '5f5dee34-2af6-4835-88ed-29690b16352a', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65658.0, 'amount': 0.01, 'cost': 656.58, 'fee': {'cost': 0.361119, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.361119, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '696c76e9-979b-4514-bc8c-dd62213477df', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'a372c55c-6d52-4cc1-9628-16a84d626503', 'stopOrderType': 'StopLoss', 'execTime': '1718398453489', 'feeCurrency': '', 'createType': 'CreateByStopLoss', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65695.7', 'execPrice': '65700', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '68983.8', 'execValue': '657', 'closedSize': '0.01', 'execType': 'Trade', 'seq': '470948219', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.36135', 'execId': '696c76e9-979b-4514-bc8c-dd62213477df', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718398453489, 'datetime': '2024-06-14T20:54:13.489Z', 'symbol': 'BTC/USDT:USDT', 'order': 'a372c55c-6d52-4cc1-9628-16a84d626503', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65700.0, 'amount': 0.01, 'cost': 657.0, 'fee': {'cost': 0.36135, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.36135, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '12c9db42-8352-484b-904e-69d9120a7b2a', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'ad1d22f1-3486-49df-a24a-2c35368ddcfc', 'stopOrderType': 'UNKNOWN', 'execTime': '1718398762032', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65719.4', 'execPrice': '65719.3', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '62433.4', 'execValue': '657.193', 'closedSize': '0', 'execType': 'Trade', 'seq': '470954507', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.36145615', 'execId': '12c9db42-8352-484b-904e-69d9120a7b2a', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718398762032, 'datetime': '2024-06-14T20:59:22.032Z', 'symbol': 'BTC/USDT:USDT', 'order': 'ad1d22f1-3486-49df-a24a-2c35368ddcfc', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65719.3, 'amount': 0.01, 'cost': 657.193, 'fee': {'cost': 0.36145615, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.36145615, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '79dd8700-1123-47cc-92d1-2b63f7364b9c', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '9279ac0b-a368-484b-994e-2ef005f883fe', 'stopOrderType': 'UNKNOWN', 'execTime': '1718402080141', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '66325.16', 'execPrice': '66318.4', 'markIv': '', 'orderQty': '0.07', 'orderPrice': '63002.5', 'execValue': '4642.288', 'closedSize': '0', 'execType': 'Trade', 'seq': '471024722', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '2.5532584', 'execId': '79dd8700-1123-47cc-92d1-2b63f7364b9c', 'marketUnit': '', 'execQty': '0.07'}, 'timestamp': 1718402080141, 'datetime': '2024-06-14T21:54:40.141Z', 'symbol': 'BTC/USDT:USDT', 'order': '9279ac0b-a368-484b-994e-2ef005f883fe', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 66318.4, 'amount': 0.07, 'cost': 4642.288, 'fee': {'cost': 2.5532584, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 2.5532584, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'eee9a0af-5f9d-41db-832c-43b1f3487b8a', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '65236458-5ba4-4ae6-9e2b-024793d452cd', 'stopOrderType': 'UNKNOWN', 'execTime': '1718402205878', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '66226.49', 'execPrice': '66230', 'markIv': '', 'orderQty': '0.07', 'orderPrice': '62918.5', 'execValue': '4636.1', 'closedSize': '0', 'execType': 'Trade', 'seq': '471027302', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '2.549855', 'execId': 'eee9a0af-5f9d-41db-832c-43b1f3487b8a', 'marketUnit': '', 'execQty': '0.07'}, 'timestamp': 1718402205878, 'datetime': '2024-06-14T21:56:45.878Z', 'symbol': 'BTC/USDT:USDT', 'order': '65236458-5ba4-4ae6-9e2b-024793d452cd', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 66230.0, 'amount': 0.07, 'cost': 4636.1, 'fee': {'cost': 2.549855, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 2.549855, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'b75ae36e-7d83-4a25-9bba-7a7376884852', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '28aea0d0-a6d9-4172-82a1-7755ac073ceb', 'stopOrderType': 'PartialTakeProfit', 'execTime': '1718402520389', 'feeCurrency': '', 'createType': 'CreateByPartialTakeProfit', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '66013.11', 'execPrice': '65894.1', 'markIv': '', 'orderQty': '0.07', 'orderPrice': '69195.7', 'execValue': '4612.587', 'closedSize': '0.07', 'execType': 'Trade', 'seq': '471033754', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '2.53692285', 'execId': 'b75ae36e-7d83-4a25-9bba-7a7376884852', 'marketUnit': '', 'execQty': '0.07'}, 'timestamp': 1718402520389, 'datetime': '2024-06-14T22:02:00.389Z', 'symbol': 'BTC/USDT:USDT', 'order': '28aea0d0-a6d9-4172-82a1-7755ac073ceb', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65894.1, 'amount': 0.07, 'cost': 4612.587, 'fee': {'cost': 2.53692285, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 2.53692285, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '75af7da3-beb5-4ef7-81ac-6898091f1bd0', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '249991e3-6460-4ca4-9ea4-4c27e41beba1', 'stopOrderType': 'UNKNOWN', 'execTime': '1718404603467', 'feeCurrency': '', 'createType': 'CreateByClosing', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65916', 'execPrice': '65910.2', 'markIv': '', 'orderQty': '0.08', 'orderPrice': '69205.7', 'execValue': '5272.816', 'closedSize': '0.08', 'execType': 'Trade', 'seq': '471077734', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '2.9000488', 'execId': '75af7da3-beb5-4ef7-81ac-6898091f1bd0', 'marketUnit': '', 'execQty': '0.08'}, 'timestamp': 1718404603467, 'datetime': '2024-06-14T22:36:43.467Z', 'symbol': 'BTC/USDT:USDT', 'order': '249991e3-6460-4ca4-9ea4-4c27e41beba1', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65910.2, 'amount': 0.08, 'cost': 5272.816, 'fee': {'cost': 2.9000488, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 2.9000488, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'c5c471be-c414-48ab-8881-187d4bb4f3be', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '6419085b-38fe-4719-9ff2-e91152d5dfad', 'stopOrderType': 'UNKNOWN', 'execTime': '1718405462133', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65964.3', 'execPrice': '65964.3', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '62666.1', 'execValue': '659.643', 'closedSize': '0', 'execType': 'Trade', 'seq': '471095283', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.36280365', 'execId': 'c5c471be-c414-48ab-8881-187d4bb4f3be', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718405462133, 'datetime': '2024-06-14T22:51:02.133Z', 'symbol': 'BTC/USDT:USDT', 'order': '6419085b-38fe-4719-9ff2-e91152d5dfad', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65964.3, 'amount': 0.01, 'cost': 659.643, 'fee': {'cost': 0.36280365, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.36280365, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'f5533196-de14-4b95-8bea-b35e0c81f4a8', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '17c256ce-f61c-44b4-bab3-05c875a7de3c', 'stopOrderType': 'UNKNOWN', 'execTime': '1718405918477', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65971.89', 'execPrice': '65969.9', 'markIv': '', 'orderQty': '0.005', 'orderPrice': '62671.5', 'execValue': '329.8495', 'closedSize': '0', 'execType': 'Trade', 'seq': '471104647', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.18141723', 'execId': 'f5533196-de14-4b95-8bea-b35e0c81f4a8', 'marketUnit': '', 'execQty': '0.005'}, 'timestamp': 1718405918477, 'datetime': '2024-06-14T22:58:38.477Z', 'symbol': 'BTC/USDT:USDT', 'order': '17c256ce-f61c-44b4-bab3-05c875a7de3c', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65969.9, 'amount': 0.005, 'cost': 329.8495, 'fee': {'cost': 0.18141723, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.18141723, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '128aea7d-567e-479b-a0a7-da5f08fc8187', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'a676d536-188b-44e1-bb84-9f29d0397d12', 'stopOrderType': 'UNKNOWN', 'execTime': '1718406183152', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65947', 'execPrice': '65947', 'markIv': '', 'orderQty': '0.04', 'orderPrice': '62649.7', 'execValue': '2637.88', 'closedSize': '0', 'execType': 'Trade', 'seq': '471110041', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '1.450834', 'execId': '128aea7d-567e-479b-a0a7-da5f08fc8187', 'marketUnit': '', 'execQty': '0.04'}, 'timestamp': 1718406183152, 'datetime': '2024-06-14T23:03:03.152Z', 'symbol': 'BTC/USDT:USDT', 'order': 'a676d536-188b-44e1-bb84-9f29d0397d12', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65947.0, 'amount': 0.04, 'cost': 2637.88, 'fee': {'cost': 1.450834, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 1.450834, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '596fb299-7ead-413d-b39b-ec3d21e4f53a', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '69aa43c0-8705-4396-8db8-e4a6216464a6', 'stopOrderType': 'UNKNOWN', 'execTime': '1718406283667', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65924.3', 'execPrice': '65924.4', 'markIv': '', 'orderQty': '0.07', 'orderPrice': '62628.2', 'execValue': '4614.708', 'closedSize': '0', 'execType': 'Trade', 'seq': '471112060', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '2.5380894', 'execId': '596fb299-7ead-413d-b39b-ec3d21e4f53a', 'marketUnit': '', 'execQty': '0.07'}, 'timestamp': 1718406283667, 'datetime': '2024-06-14T23:04:43.667Z', 'symbol': 'BTC/USDT:USDT', 'order': '69aa43c0-8705-4396-8db8-e4a6216464a6', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65924.4, 'amount': 0.07, 'cost': 4614.708, 'fee': {'cost': 2.5380894, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 2.5380894, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'e51f4096-9bd9-41d6-9f9d-e1fb35757fc1', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '7856b683-2081-46e8-b0f5-790c35e22e1e', 'stopOrderType': 'UNKNOWN', 'execTime': '1718406414424', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65895.3', 'execPrice': '65895.3', 'markIv': '', 'orderQty': '0.04', 'orderPrice': '62600.6', 'execValue': '2635.812', 'closedSize': '0', 'execType': 'Trade', 'seq': '471114743', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '1.4496966', 'execId': 'e51f4096-9bd9-41d6-9f9d-e1fb35757fc1', 'marketUnit': '', 'execQty': '0.04'}, 'timestamp': 1718406414424, 'datetime': '2024-06-14T23:06:54.424Z', 'symbol': 'BTC/USDT:USDT', 'order': '7856b683-2081-46e8-b0f5-790c35e22e1e', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65895.3, 'amount': 0.04, 'cost': 2635.812, 'fee': {'cost': 1.4496966, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 1.4496966, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'afac1f82-1ba3-4d4f-9f5c-fbe48fea7c39', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '56bb0911-1775-4ae7-9fd5-43137043c79e', 'stopOrderType': 'PartialStopLoss', 'execTime': '1718407556369', 'feeCurrency': '', 'createType': 'CreateByPartialStopLoss', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '66014.4', 'execPrice': '66023.5', 'markIv': '', 'orderQty': '0.005', 'orderPrice': '69322', 'execValue': '330.1175', 'closedSize': '0.005', 'execType': 'Trade', 'seq': '471138113', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.18156463', 'execId': 'afac1f82-1ba3-4d4f-9f5c-fbe48fea7c39', 'marketUnit': '', 'execQty': '0.005'}, 'timestamp': 1718407556369, 'datetime': '2024-06-14T23:25:56.369Z', 'symbol': 'BTC/USDT:USDT', 'order': '56bb0911-1775-4ae7-9fd5-43137043c79e', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 66023.5, 'amount': 0.005, 'cost': 330.1175, 'fee': {'cost': 0.18156463, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.18156463, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '0d0c76f2-ae62-4c2a-a206-306263bc23cf', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '849b4c0b-69c1-4500-aaac-ae35e8ca3a4e', 'stopOrderType': 'UNKNOWN', 'execTime': '1718408784375', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65978.8', 'execPrice': '65978.8', 'markIv': '', 'orderQty': '0.07', 'orderPrice': '62679.9', 'execValue': '4618.516', 'closedSize': '0', 'execType': 'Trade', 'seq': '471163089', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '2.5401838', 'execId': '0d0c76f2-ae62-4c2a-a206-306263bc23cf', 'marketUnit': '', 'execQty': '0.07'}, 'timestamp': 1718408784375, 'datetime': '2024-06-14T23:46:24.375Z', 'symbol': 'BTC/USDT:USDT', 'order': '849b4c0b-69c1-4500-aaac-ae35e8ca3a4e', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65978.8, 'amount': 0.07, 'cost': 4618.516, 'fee': {'cost': 2.5401838, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 2.5401838, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'bce02253-dffd-4c3a-81ab-143380e0a84e', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'a68570d0-ef2b-468b-8967-dcf8f64356c0', 'stopOrderType': 'UNKNOWN', 'execTime': '1718409878354', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '66015.75', 'execPrice': '66014', 'markIv': '', 'orderQty': '0.07', 'orderPrice': '65850', 'execValue': '4620.98', 'closedSize': '0', 'execType': 'Trade', 'seq': '471186349', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '2.541539', 'execId': 'bce02253-dffd-4c3a-81ab-143380e0a84e', 'marketUnit': '', 'execQty': '0.07'}, 'timestamp': 1718409878354, 'datetime': '2024-06-15T00:04:38.354Z', 'symbol': 'BTC/USDT:USDT', 'order': 'a68570d0-ef2b-468b-8967-dcf8f64356c0', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 66014.0, 'amount': 0.07, 'cost': 4620.98, 'fee': {'cost': 2.541539, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 2.541539, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '1ba1fce2-54af-4093-a6d4-29924e9d2a0a', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '2d47563d-e9a5-42ef-88d0-4bdee4dd5e82', 'stopOrderType': 'PartialTakeProfit', 'execTime': '1718482764310', 'feeCurrency': '', 'createType': 'CreateByPartialTakeProfit', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65984.8', 'execPrice': '65936.3', 'markIv': '', 'orderQty': '0.07', 'orderPrice': '69235.7', 'execValue': '4615.541', 'closedSize': '0.07', 'execType': 'Trade', 'seq': '472705264', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '2.53854755', 'execId': '1ba1fce2-54af-4093-a6d4-29924e9d2a0a', 'marketUnit': '', 'execQty': '0.07'}, 'timestamp': 1718482764310, 'datetime': '2024-06-15T20:19:24.310Z', 'symbol': 'BTC/USDT:USDT', 'order': '2d47563d-e9a5-42ef-88d0-4bdee4dd5e82', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65936.3, 'amount': 0.07, 'cost': 4615.541, 'fee': {'cost': 2.53854755, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 2.53854755, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'a0fed4b8-682d-472a-933f-87b2c4959475', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '969d2942-6770-4606-a5b2-b0eef8784d18', 'stopOrderType': 'PartialTakeProfit', 'execTime': '1718618191891', 'feeCurrency': '', 'createType': 'CreateByPartialTakeProfit', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65861.1', 'execPrice': '65800', 'markIv': '', 'orderQty': '0.04', 'orderPrice': '69090.2', 'execValue': '2632', 'closedSize': '0.04', 'execType': 'Trade', 'seq': '475537931', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '1.4476', 'execId': 'a0fed4b8-682d-472a-933f-87b2c4959475', 'marketUnit': '', 'execQty': '0.04'}, 'timestamp': 1718618191891, 'datetime': '2024-06-17T09:56:31.891Z', 'symbol': 'BTC/USDT:USDT', 'order': '969d2942-6770-4606-a5b2-b0eef8784d18', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65800.0, 'amount': 0.04, 'cost': 2632.0, 'fee': {'cost': 1.4476, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 1.4476, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '713b9201-09da-42aa-bc3a-d1cf8301a2f1', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'f8a2e87d-05fe-4980-ba71-9fa9e7ddd12d', 'stopOrderType': 'UNKNOWN', 'execTime': '1718669816419', 'feeCurrency': '', 'createType': 'CreateByClosing', 'feeRate': '0.0002', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '66377.84', 'execPrice': '66376.7', 'markIv': '', 'orderQty': '0.09', 'orderPrice': '66376.7', 'execValue': '5973.903', 'closedSize': '0.09', 'execType': 'Trade', 'seq': '476624967', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': True, 'execFee': '1.1947806', 'execId': '713b9201-09da-42aa-bc3a-d1cf8301a2f1', 'marketUnit': '', 'execQty': '0.09'}, 'timestamp': 1718669816419, 'datetime': '2024-06-18T00:16:56.419Z', 'symbol': 'BTC/USDT:USDT', 'order': 'f8a2e87d-05fe-4980-ba71-9fa9e7ddd12d', 'type': 'limit', 'side': 'buy', 'takerOrMaker': 'maker', 'price': 66376.7, 'amount': 0.09, 'cost': 5973.903, 'fee': {'cost': 1.1947806, 'currency': 'USDT', 'rate': 0.0002}, 'fees': [{'cost': 1.1947806, 'currency': 'USDT', 'rate': 0.0002}]}, {'id': '0b7f6282-1055-4c36-8e95-f42dfc4da345', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'f439ed8a-a42e-47e1-a98c-374b6714da78', 'stopOrderType': 'PartialTakeProfit', 'execTime': '1718673814829', 'feeCurrency': '', 'createType': 'CreateByPartialTakeProfit', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65478.63', 'execPrice': '65430.2', 'markIv': '', 'orderQty': '0.1', 'orderPrice': '68738.9', 'execValue': '6543.02', 'closedSize': '0.1', 'execType': 'Trade', 'seq': '476708660', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '3.598661', 'execId': '0b7f6282-1055-4c36-8e95-f42dfc4da345', 'marketUnit': '', 'execQty': '0.1'}, 'timestamp': 1718673814829, 'datetime': '2024-06-18T01:23:34.829Z', 'symbol': 'BTC/USDT:USDT', 'order': 'f439ed8a-a42e-47e1-a98c-374b6714da78', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65430.2, 'amount': 0.1, 'cost': 6543.02, 'fee': {'cost': 3.598661, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 3.598661, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'dc05b398-47b8-4a3c-8d17-1366e4d03bd2', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'a630cf78-d0c9-439c-895f-8df9e6129d2f', 'stopOrderType': 'Stop', 'execTime': '1718677898359', 'feeCurrency': '', 'createType': 'CreateByStopOrder', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65332.9', 'execPrice': '65322', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '64503', 'execValue': '653.22', 'closedSize': '0', 'execType': 'Trade', 'seq': '476799813', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.359271', 'execId': 'dc05b398-47b8-4a3c-8d17-1366e4d03bd2', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718677898359, 'datetime': '2024-06-18T02:31:38.359Z', 'symbol': 'BTC/USDT:USDT', 'order': 'a630cf78-d0c9-439c-895f-8df9e6129d2f', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65322.0, 'amount': 0.01, 'cost': 653.22, 'fee': {'cost': 0.359271, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.359271, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '76906fe1-da92-4fce-afd3-af72695223b7', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '48969f91-3dc9-425d-9feb-3705a697c82b', 'stopOrderType': 'UNKNOWN', 'execTime': '1718677975701', 'feeCurrency': '', 'createType': 'CreateByClosing', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65367.1', 'execPrice': '65371.2', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '68639.7', 'execValue': '653.712', 'closedSize': '0.01', 'execType': 'Trade', 'seq': '476801391', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.3595416', 'execId': '76906fe1-da92-4fce-afd3-af72695223b7', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718677975701, 'datetime': '2024-06-18T02:32:55.701Z', 'symbol': 'BTC/USDT:USDT', 'order': '48969f91-3dc9-425d-9feb-3705a697c82b', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65371.2, 'amount': 0.01, 'cost': 653.712, 'fee': {'cost': 0.3595416, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.3595416, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '18b60c6c-8880-49f6-9254-34be9b765c24', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'aff2ded1-a254-4876-bcc2-afcbc7eea23b', 'stopOrderType': 'Stop', 'execTime': '1718751484399', 'feeCurrency': '', 'createType': 'CreateByStopOrder', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65237.6', 'execPrice': '65236.2', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '65040', 'execValue': '652.362', 'closedSize': '0', 'execType': 'Trade', 'seq': '478354971', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.3587991', 'execId': '18b60c6c-8880-49f6-9254-34be9b765c24', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718751484399, 'datetime': '2024-06-18T22:58:04.399Z', 'symbol': 'BTC/USDT:USDT', 'order': 'aff2ded1-a254-4876-bcc2-afcbc7eea23b', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65236.2, 'amount': 0.01, 'cost': 652.362, 'fee': {'cost': 0.3587991, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.3587991, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '19edc187-84e6-43d4-955f-07226999c049', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '11a17248-7f56-4b66-8f72-44ea47c6fa89', 'stopOrderType': 'UNKNOWN', 'execTime': '1718751703101', 'feeCurrency': '', 'createType': 'CreateByClosing', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65232.64', 'execPrice': '65230.3', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '68491.8', 'execValue': '652.303', 'closedSize': '0.01', 'execType': 'Trade', 'seq': '478359442', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.35876665', 'execId': '19edc187-84e6-43d4-955f-07226999c049', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718751703101, 'datetime': '2024-06-18T23:01:43.101Z', 'symbol': 'BTC/USDT:USDT', 'order': '11a17248-7f56-4b66-8f72-44ea47c6fa89', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65230.3, 'amount': 0.01, 'cost': 652.303, 'fee': {'cost': 0.35876665, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.35876665, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '49b80287-273e-4180-961d-1c8f44b445ac', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '9dbf6298-5b05-41a4-a519-40bd977afc15', 'stopOrderType': 'Stop', 'execTime': '1718751994629', 'feeCurrency': '', 'createType': 'CreateByStopOrder', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65136.91', 'execPrice': '65130.4', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '64990', 'execValue': '651.304', 'closedSize': '0', 'execType': 'Trade', 'seq': '478365391', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.3582172', 'execId': '49b80287-273e-4180-961d-1c8f44b445ac', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718751994629, 'datetime': '2024-06-18T23:06:34.629Z', 'symbol': 'BTC/USDT:USDT', 'order': '9dbf6298-5b05-41a4-a519-40bd977afc15', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65130.4, 'amount': 0.01, 'cost': 651.304, 'fee': {'cost': 0.3582172, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.3582172, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '904a76d0-bfc4-43d0-b6fb-be4437fb8305', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '36e56d25-627e-48bb-af15-bc68014fe803', 'stopOrderType': 'UNKNOWN', 'execTime': '1718752198686', 'feeCurrency': '', 'createType': 'CreateByClosing', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65144.77', 'execPrice': '65141.5', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '68398.5', 'execValue': '651.415', 'closedSize': '0.01', 'execType': 'Trade', 'seq': '478369565', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.35827825', 'execId': '904a76d0-bfc4-43d0-b6fb-be4437fb8305', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718752198686, 'datetime': '2024-06-18T23:09:58.686Z', 'symbol': 'BTC/USDT:USDT', 'order': '36e56d25-627e-48bb-af15-bc68014fe803', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65141.5, 'amount': 0.01, 'cost': 651.415, 'fee': {'cost': 0.35827825, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.35827825, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '47aa8ed3-10fe-4cc4-b813-8bdd046db1e1', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '3f018211-c6ee-4757-b3c5-b81acdf3e343', 'stopOrderType': 'Stop', 'execTime': '1718752371950', 'feeCurrency': '', 'createType': 'CreateByStopOrder', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65108', 'execPrice': '65100', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '64930', 'execValue': '651', 'closedSize': '0', 'execType': 'Trade', 'seq': '478373113', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.35805', 'execId': '47aa8ed3-10fe-4cc4-b813-8bdd046db1e1', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718752371950, 'datetime': '2024-06-18T23:12:51.950Z', 'symbol': 'BTC/USDT:USDT', 'order': '3f018211-c6ee-4757-b3c5-b81acdf3e343', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65100.0, 'amount': 0.01, 'cost': 651.0, 'fee': {'cost': 0.35805, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.35805, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '30d8f75a-31fe-4de8-a1a3-99296a253741', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '00d2cf5d-8676-4eb6-8041-d0f7375a0d6c', 'stopOrderType': 'PartialStopLoss', 'execTime': '1718754132499', 'feeCurrency': '', 'createType': 'CreateByPartialStopLoss', 'feeRate': '0.0002', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65110.58', 'execPrice': '65105.7', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '65105.7', 'execValue': '651.057', 'closedSize': '0.01', 'execType': 'Trade', 'seq': '478409740', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': True, 'execFee': '0.1302114', 'execId': '30d8f75a-31fe-4de8-a1a3-99296a253741', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718754132499, 'datetime': '2024-06-18T23:42:12.499Z', 'symbol': 'BTC/USDT:USDT', 'order': '00d2cf5d-8676-4eb6-8041-d0f7375a0d6c', 'type': 'limit', 'side': 'buy', 'takerOrMaker': 'maker', 'price': 65105.7, 'amount': 0.01, 'cost': 651.057, 'fee': {'cost': 0.1302114, 'currency': 'USDT', 'rate': 0.0002}, 'fees': [{'cost': 0.1302114, 'currency': 'USDT', 'rate': 0.0002}]}, {'id': '3878d09c-0d22-44c4-8831-587f17550bf2', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '6484ee2b-bf21-4f3d-8a0a-5503576b28a6', 'stopOrderType': 'Stop', 'execTime': '1718754631823', 'feeCurrency': '', 'createType': 'CreateByStopOrder', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65072.14', 'execPrice': '65070', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '65090', 'execValue': '650.7', 'closedSize': '0', 'execType': 'Trade', 'seq': '478419960', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.357885', 'execId': '3878d09c-0d22-44c4-8831-587f17550bf2', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718754631823, 'datetime': '2024-06-18T23:50:31.823Z', 'symbol': 'BTC/USDT:USDT', 'order': '6484ee2b-bf21-4f3d-8a0a-5503576b28a6', 'type': 'limit', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65070.0, 'amount': 0.01, 'cost': 650.7, 'fee': {'cost': 0.357885, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.357885, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '8ec1c7d7-19f8-4341-bc32-f3d35375080c', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '39fa31d5-3c26-4aeb-ae43-38838b468d01', 'stopOrderType': 'PartialStopLoss', 'execTime': '1718756451639', 'feeCurrency': '', 'createType': 'CreateByPartialStopLoss', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '64905', 'execPrice': '64892.8', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '64885', 'execValue': '648.928', 'closedSize': '0.01', 'execType': 'Trade', 'seq': '478457899', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.3569104', 'execId': '8ec1c7d7-19f8-4341-bc32-f3d35375080c', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718756451639, 'datetime': '2024-06-19T00:20:51.639Z', 'symbol': 'BTC/USDT:USDT', 'order': '39fa31d5-3c26-4aeb-ae43-38838b468d01', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 64892.8, 'amount': 0.01, 'cost': 648.928, 'fee': {'cost': 0.3569104, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.3569104, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '6bffcb33-04cf-4a32-8ad4-bf05e2c5b81c', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '4ce2abbe-b864-4876-bdd5-91d7dcdd20ae', 'stopOrderType': 'Stop', 'execTime': '1718757107039', 'feeCurrency': '', 'createType': 'CreateByStopOrder', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '64876.27', 'execPrice': '64880.4', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '64990', 'execValue': '648.804', 'closedSize': '0', 'execType': 'Trade', 'seq': '478472102', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.3568422', 'execId': '6bffcb33-04cf-4a32-8ad4-bf05e2c5b81c', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718757107039, 'datetime': '2024-06-19T00:31:47.039Z', 'symbol': 'BTC/USDT:USDT', 'order': '4ce2abbe-b864-4876-bdd5-91d7dcdd20ae', 'type': 'limit', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 64880.4, 'amount': 0.01, 'cost': 648.804, 'fee': {'cost': 0.3568422, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.3568422, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '3bd10016-aaf5-4678-9c64-9a4785013907', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'e21bef9e-f439-4779-a025-e04280e6deaa', 'stopOrderType': 'PartialTakeProfit', 'execTime': '1718757309409', 'feeCurrency': '', 'createType': 'CreateByPartialTakeProfit', 'feeRate': '0.0002', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '64921.71', 'execPrice': '64921.8', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '64921.8', 'execValue': '649.218', 'closedSize': '0.01', 'execType': 'Trade', 'seq': '478476236', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': True, 'execFee': '0.1298436', 'execId': '3bd10016-aaf5-4678-9c64-9a4785013907', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718757309409, 'datetime': '2024-06-19T00:35:09.409Z', 'symbol': 'BTC/USDT:USDT', 'order': 'e21bef9e-f439-4779-a025-e04280e6deaa', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'maker', 'price': 64921.8, 'amount': 0.01, 'cost': 649.218, 'fee': {'cost': 0.1298436, 'currency': 'USDT', 'rate': 0.0002}, 'fees': [{'cost': 0.1298436, 'currency': 'USDT', 'rate': 0.0002}]}, {'id': '787b7705-e9e9-4574-9ca4-122b27a9b1ce', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'ab78a58c-dd5a-4229-94dd-fb6549362846', 'stopOrderType': 'UNKNOWN', 'execTime': '1718758870904', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65195.5', 'execPrice': '65199.8', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '68459.7', 'execValue': '651.998', 'closedSize': '0', 'execType': 'Trade', 'seq': '478508692', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.3585989', 'execId': '787b7705-e9e9-4574-9ca4-122b27a9b1ce', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718758870904, 'datetime': '2024-06-19T01:01:10.904Z', 'symbol': 'BTC/USDT:USDT', 'order': 'ab78a58c-dd5a-4229-94dd-fb6549362846', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65199.8, 'amount': 0.01, 'cost': 651.998, 'fee': {'cost': 0.3585989, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.3585989, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '26601901-5437-4ad5-8536-dbf1a94d95b8', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '9b7e9a0c-28e7-4dfe-a38f-0b1e2b5d5065', 'stopOrderType': 'PartialTakeProfit', 'execTime': '1718759072249', 'feeCurrency': '', 'createType': 'CreateByPartialTakeProfit', 'feeRate': '0.0002', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65296.69', 'execPrice': '65301', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '65301', 'execValue': '653.01', 'closedSize': '0.01', 'execType': 'Trade', 'seq': '478512952', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': True, 'execFee': '0.130602', 'execId': '26601901-5437-4ad5-8536-dbf1a94d95b8', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718759072249, 'datetime': '2024-06-19T01:04:32.249Z', 'symbol': 'BTC/USDT:USDT', 'order': '9b7e9a0c-28e7-4dfe-a38f-0b1e2b5d5065', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'maker', 'price': 65301.0, 'amount': 0.01, 'cost': 653.01, 'fee': {'cost': 0.130602, 'currency': 'USDT', 'rate': 0.0002}, 'fees': [{'cost': 0.130602, 'currency': 'USDT', 'rate': 0.0002}]}, {'id': '36d6c041-b2cc-433b-a465-75695d462c0b', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '8c8c18c9-9317-4d12-9afa-d50bdee2ca42', 'stopOrderType': 'UNKNOWN', 'execTime': '1718760625915', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65128.57', 'execPrice': '65119.2', 'markIv': '', 'orderQty': '0.1', 'orderPrice': '65140', 'execValue': '6511.92', 'closedSize': '0', 'execType': 'Trade', 'seq': '478545934', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '3.581556', 'execId': '36d6c041-b2cc-433b-a465-75695d462c0b', 'marketUnit': '', 'execQty': '0.1'}, 'timestamp': 1718760625915, 'datetime': '2024-06-19T01:30:25.915Z', 'symbol': 'BTC/USDT:USDT', 'order': '8c8c18c9-9317-4d12-9afa-d50bdee2ca42', 'type': 'limit', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65119.2, 'amount': 0.1, 'cost': 6511.92, 'fee': {'cost': 3.581556, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 3.581556, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '9f3e6a08-8073-4cff-b209-5380f3c0de53', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'fdd75eab-63ab-4636-959a-0986cb233af4', 'stopOrderType': 'PartialStopLoss', 'execTime': '1718760801819', 'feeCurrency': '', 'createType': 'CreateByPartialStopLoss', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '64950.6', 'execPrice': '64935.8', 'markIv': '', 'orderQty': '0.1', 'orderPrice': '64935', 'execValue': '6493.58', 'closedSize': '0.1', 'execType': 'Trade', 'seq': '478549625', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '3.571469', 'execId': '9f3e6a08-8073-4cff-b209-5380f3c0de53', 'marketUnit': '', 'execQty': '0.1'}, 'timestamp': 1718760801819, 'datetime': '2024-06-19T01:33:21.819Z', 'symbol': 'BTC/USDT:USDT', 'order': 'fdd75eab-63ab-4636-959a-0986cb233af4', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 64935.8, 'amount': 0.1, 'cost': 6493.58, 'fee': {'cost': 3.571469, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 3.571469, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'fa0ba27d-4eee-4252-834d-0db98549bdc7', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'b7efc31c-5201-4680-b055-b32c2389ac9b', 'stopOrderType': 'UNKNOWN', 'execTime': '1718762490279', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65049.5', 'execPrice': '65049.5', 'markIv': '', 'orderQty': '0.3', 'orderPrice': '68301.9', 'execValue': '19514.85', 'closedSize': '0', 'execType': 'Trade', 'seq': '478585144', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '10.7331675', 'execId': 'fa0ba27d-4eee-4252-834d-0db98549bdc7', 'marketUnit': '', 'execQty': '0.3'}, 'timestamp': 1718762490279, 'datetime': '2024-06-19T02:01:30.279Z', 'symbol': 'BTC/USDT:USDT', 'order': 'b7efc31c-5201-4680-b055-b32c2389ac9b', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 65049.5, 'amount': 0.3, 'cost': 19514.85, 'fee': {'cost': 10.7331675, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 10.7331675, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '3b1b12a8-c251-487f-a203-bc6280605381', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '152d7f4b-32a5-4699-8b1d-d059e8602e76', 'stopOrderType': 'Stop', 'execTime': '1718762762369', 'feeCurrency': '', 'createType': 'CreateByStopOrder', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65170.25', 'execPrice': '65170.1', 'markIv': '', 'orderQty': '0.01', 'orderPrice': '61911.5', 'execValue': '651.701', 'closedSize': '0.01', 'execType': 'Trade', 'seq': '478590769', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.35843555', 'execId': '3b1b12a8-c251-487f-a203-bc6280605381', 'marketUnit': '', 'execQty': '0.01'}, 'timestamp': 1718762762369, 'datetime': '2024-06-19T02:06:02.369Z', 'symbol': 'BTC/USDT:USDT', 'order': '152d7f4b-32a5-4699-8b1d-d059e8602e76', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65170.1, 'amount': 0.01, 'cost': 651.701, 'fee': {'cost': 0.35843555, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.35843555, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'c9749d70-b911-443d-a352-9f6e14d5bda4', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'f5cf58d5-6aa5-4d00-a60d-543be5027cab', 'stopOrderType': 'Stop', 'execTime': '1718762917099', 'feeCurrency': '', 'createType': 'CreateByStopOrder', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65170.99', 'execPrice': '65176.5', 'markIv': '', 'orderQty': '0.02', 'orderPrice': '61917.5', 'execValue': '1303.53', 'closedSize': '0.02', 'execType': 'Trade', 'seq': '478593957', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '0.7169415', 'execId': 'c9749d70-b911-443d-a352-9f6e14d5bda4', 'marketUnit': '', 'execQty': '0.02'}, 'timestamp': 1718762917099, 'datetime': '2024-06-19T02:08:37.099Z', 'symbol': 'BTC/USDT:USDT', 'order': 'f5cf58d5-6aa5-4d00-a60d-543be5027cab', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 65176.5, 'amount': 0.02, 'cost': 1303.53, 'fee': {'cost': 0.7169415, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 0.7169415, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'd520874a-5cc4-4fff-a455-385b73e2f8d9', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'ad412204-c9f6-4a8f-8352-d3c0f3d1dbd1', 'stopOrderType': 'PartialTakeProfit', 'execTime': '1718763362489', 'feeCurrency': '', 'createType': 'CreateByPartialTakeProfit', 'feeRate': '0.0002', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65218.6', 'execPrice': '65225', 'markIv': '', 'orderQty': '0.25', 'orderPrice': '65225', 'execValue': '16306.25', 'closedSize': '0.25', 'execType': 'Trade', 'seq': '478603188', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': True, 'execFee': '3.26125', 'execId': 'd520874a-5cc4-4fff-a455-385b73e2f8d9', 'marketUnit': '', 'execQty': '0.25'}, 'timestamp': 1718763362489, 'datetime': '2024-06-19T02:16:02.489Z', 'symbol': 'BTC/USDT:USDT', 'order': 'ad412204-c9f6-4a8f-8352-d3c0f3d1dbd1', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'maker', 'price': 65225.0, 'amount': 0.25, 'cost': 16306.25, 'fee': {'cost': 3.26125, 'currency': 'USDT', 'rate': 0.0002}, 'fees': [{'cost': 3.26125, 'currency': 'USDT', 'rate': 0.0002}]}, {'id': 'ee3de7da-9877-4e34-8a55-46204ef4f2c0', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '500b8178-fa01-4606-b6e2-3b451d70b1d7', 'stopOrderType': 'PartialTakeProfit', 'execTime': '1718763448079', 'feeCurrency': '', 'createType': 'CreateByPartialTakeProfit', 'feeRate': '0.0002', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '65247.9', 'execPrice': '65250', 'markIv': '', 'orderQty': '0.02', 'orderPrice': '65250', 'execValue': '1305', 'closedSize': '0.02', 'execType': 'Trade', 'seq': '478604949', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': True, 'execFee': '0.261', 'execId': 'ee3de7da-9877-4e34-8a55-46204ef4f2c0', 'marketUnit': '', 'execQty': '0.02'}, 'timestamp': 1718763448079, 'datetime': '2024-06-19T02:17:28.079Z', 'symbol': 'BTC/USDT:USDT', 'order': '500b8178-fa01-4606-b6e2-3b451d70b1d7', 'type': 'limit', 'side': 'sell', 'takerOrMaker': 'maker', 'price': 65250.0, 'amount': 0.02, 'cost': 1305.0, 'fee': {'cost': 0.261, 'currency': 'USDT', 'rate': 0.0002}, 'fees': [{'cost': 0.261, 'currency': 'USDT', 'rate': 0.0002}]}, {'id': '96b5fb86-9f45-476f-8daf-865399713574', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': 'd6d09e63-122e-445f-b43d-216e2f64166b', 'stopOrderType': 'UNKNOWN', 'execTime': '1718829476354', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '64802.26', 'execPrice': '64800.4', 'markIv': '', 'orderQty': '0.1', 'orderPrice': '68040.4', 'execValue': '6480.04', 'closedSize': '0', 'execType': 'Trade', 'seq': '479992568', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '3.564022', 'execId': '96b5fb86-9f45-476f-8daf-865399713574', 'marketUnit': '', 'execQty': '0.1'}, 'timestamp': 1718829476354, 'datetime': '2024-06-19T20:37:56.354Z', 'symbol': 'BTC/USDT:USDT', 'order': 'd6d09e63-122e-445f-b43d-216e2f64166b', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 64800.4, 'amount': 0.1, 'cost': 6480.04, 'fee': {'cost': 3.564022, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 3.564022, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'c3b015d3-49ee-4a26-a2e0-be177fcdd9e4', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '0c85670a-a0ff-4166-99a5-935428c109a1', 'stopOrderType': 'TrailingStop', 'execTime': '1718832018979', 'feeCurrency': '', 'createType': 'CreateByTrailingStop', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '64982.3', 'execPrice': '64977', 'markIv': '', 'orderQty': '0.1', 'orderPrice': '61730.9', 'execValue': '6497.7', 'closedSize': '0.1', 'execType': 'Trade', 'seq': '480045101', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '3.573735', 'execId': 'c3b015d3-49ee-4a26-a2e0-be177fcdd9e4', 'marketUnit': '', 'execQty': '0.1'}, 'timestamp': 1718832018979, 'datetime': '2024-06-19T21:20:18.979Z', 'symbol': 'BTC/USDT:USDT', 'order': '0c85670a-a0ff-4166-99a5-935428c109a1', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 64977.0, 'amount': 0.1, 'cost': 6497.7, 'fee': {'cost': 3.573735, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 3.573735, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': 'bb2e36c3-6f4e-47de-8f13-38c898cf9856', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '8e7a99b3-1cbb-448f-bfff-141a885690df', 'stopOrderType': 'UNKNOWN', 'execTime': '1718834373315', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '64995.8', 'execPrice': '64995.8', 'markIv': '', 'orderQty': '0.1', 'orderPrice': '61746.1', 'execValue': '6499.58', 'closedSize': '0', 'execType': 'Trade', 'seq': '480093546', 'side': 'Sell', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '3.574769', 'execId': 'bb2e36c3-6f4e-47de-8f13-38c898cf9856', 'marketUnit': '', 'execQty': '0.1'}, 'timestamp': 1718834373315, 'datetime': '2024-06-19T21:59:33.315Z', 'symbol': 'BTC/USDT:USDT', 'order': '8e7a99b3-1cbb-448f-bfff-141a885690df', 'type': 'market', 'side': 'sell', 'takerOrMaker': 'taker', 'price': 64995.8, 'amount': 0.1, 'cost': 6499.58, 'fee': {'cost': 3.574769, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 3.574769, 'currency': 'USDT', 'rate': 0.00055}]}, {'id': '7e7c19cf-ec2a-46fd-aedd-97f585748c62', 'info': {'symbol': 'BTCUSDT', 'orderType': 'Limit', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '96d6c7ef-b5d0-4f44-a79c-5aeccbe663b4', 'stopOrderType': 'PartialTakeProfit', 'execTime': '1718837345189', 'feeCurrency': '', 'createType': 'CreateByPartialTakeProfit', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '64899', 'execPrice': '64895', 'markIv': '', 'orderQty': '0.03', 'orderPrice': '64895.8', 'execValue': '1946.85', 'closedSize': '0.03', 'execType': 'Trade', 'seq': '480155496', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '1.0707675', 'execId': '7e7c19cf-ec2a-46fd-aedd-97f585748c62', 'marketUnit': '', 'execQty': '0.03'}, 'timestamp': 1718837345189, 'datetime': '2024-06-19T22:49:05.189Z', 'symbol': 'BTC/USDT:USDT', 'order': '96d6c7ef-b5d0-4f44-a79c-5aeccbe663b4', 'type': 'limit', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 64895.0, 'amount': 0.03, 'cost': 1946.85, 'fee': {'cost': 1.0707675, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 1.0707675, 'currency': 'USDT', 'rate': 0.00055}]}, 
 
 
 {'id': '1e79dc5d-c711-4f22-9e66-4ee57aa90ebc', 
 'info': {
 'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 'orderId': '23931c76-7066-4545-b77c-455d00d23407', 'stopOrderType': 'UNKNOWN', 'execTime': '1718838516464', 'feeCurrency': '', 'createType': 'CreateByClosing', 'feeRate': '0.00055', 'tradeIv': '', 'blockTradeId': '', 'markPrice': '64866.4', 'execPrice': '64866.1', 'markIv': '', 'orderQty': '0.07', 'orderPrice': '68109.4', 'execValue': '4540.627', 'closedSize': '0.07', 'execType': 'Trade', 'seq': '480179723', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 'execFee': '2.49734485', 'execId': '1e79dc5d-c711-4f22-9e66-4ee57aa90ebc', 'marketUnit': '', 'execQty': '0.07'}, 
 'timestamp': 1718838516464, 'datetime': '2024-06-19T23:08:36.464Z', 'symbol': 'BTC/USDT:USDT', 'order': '23931c76-7066-4545-b77c-455d00d23407', 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 64866.1, 'amount': 0.07, 'cost': 4540.627, 
 'fee': {'cost': 2.49734485, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 2.49734485, 'currency': 'USDT', 'rate': 0.00055}]
 }, 
 
 
 {'id': '804b3167-cd96-4d3c-94be-9fea5f02540f', 
 'info': {
 'symbol': 'BTCUSDT', 'orderType': 'Market', 'underlyingPrice': '', 'orderLinkId': '', 
 'orderId': '133ab8b2-2b5e-42c5-b300-37f1c6e0fd6b', 
 'stopOrderType': 'UNKNOWN', 'execTime': '1718839000875', 'feeCurrency': '', 'createType': 'CreateByUser', 'feeRate': '0.00055', 'tradeIv': '', 
 'blockTradeId': '', 'markPrice': '64907.2', 'execPrice': '64907.2', 'markIv': '', 
 'orderQty': '0.1', 'orderPrice': '68152.5', 'execValue': '6490.72', 'closedSize': '0', 'execType': 'Trade', 
 'seq': '480189660', 'side': 'Buy', 'indexPrice': '', 'leavesQty': '0', 'isMaker': False, 
 'execFee': '3.569896', 'execId': '804b3167-cd96-4d3c-94be-9fea5f02540f', 
 'marketUnit': '', 'execQty': '0.1', 'nextPageCursor': '380429%3A1%2C181807%3A1'
 }, 
 'timestamp': 1718839000875, 'datetime': '2024-06-19T23:16:40.875Z', 
 'symbol': 'BTC/USDT:USDT', 'order': '133ab8b2-2b5e-42c5-b300-37f1c6e0fd6b', 
 'type': 'market', 'side': 'buy', 'takerOrMaker': 'taker', 'price': 64907.2, 'amount': 0.1, 
 'cost': 6490.72, 
 'fee': {'cost': 3.569896, 'currency': 'USDT', 'rate': 0.00055}, 'fees': [{'cost': 3.569896, 'currency': 'USDT', 'rate': 0.00055}]
 }
 ]
 
 """