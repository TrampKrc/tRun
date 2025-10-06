
import traceback
import p_common as P, TMessage as M
from pprint import pprint

import re

from TMessage import OrderStatus

channel_name = "Crypto Pump Club Official"
def parser(monitor, telegram_msg ):

    telegram_msg_text = P.msg_text( telegram_msg )
    try:
        # the msg is not empty and msg.date has been checked
        if (monitor.cfg_section.get("UserId", 0) == 0 or
            monitor.cfg_section["UserId"] == telegram_msg.from_user.id):

            if order_data := text_parser(monitor, telegram_msg_text ) :
                if order_data.status == M.OrderStatus.Rejected:
                    monitor.logError(f"parser rejected to create the order from msg: {telegram_msg.text}")
                    return None

                # additional processing of parser_msg

                return order_data

    except Exception as e:
        monitor.logError(f"Unexpected parser exception {e=}, {type(e)=}")
        monitor.logError( telegram_msg_text )
        monitor.logError( traceback.format_exc(2, chain=True) )

    monitor.logError(f"parser for Channel '{telegram_msg.chat.title}' is not implemented")
    return None

def text_parser( monitor, atext ) -> M.Order_Info:

 # " 📍Coin : #AWE/USDT  🟢 LONG   ➡️ Entry: 0.1191 - 0.1160  🌐 Leverage: 20x  😵 Target 1: 0.1202 😵 Target 2: 0.1214 😵 Target 3: 0.1226 😵 Target 4: 0.1238 😵 Target 5: 0.1250 😵 Target 6: 0.1273  ❌ StopLoss: 0.1127"
    def parse_1():
        pattern = (
            r'Coin\s*:\s*#(?P<sym>\w+/\w+)\s+'
            r'.*?(?P<side>LONG|SHORT)\s+'
            r'.*?Entry:\s*(?P<entry1>[\d\.]+)\s*-\s*(?P<entry2>[\d\.]+)\s+'
            r'.*?Leverage:\s*(?P<leverage>\d+)x\s+'
            r'(?P<tp>(?:😵\s*Target\s*\d+:\s*[\d\.]+\s*)+).*?'
            r'StopLoss:\s*(?P<stloss>[\d\.]+)'
        )

        (px, pxd) = P.comp_line(pattern, atext)
        print("pattern= ", pxd)

        if len(px) != 7:
            return (None, None)

# pxd['tp'] ='😵 Target 1: 0.1202 😵 Target 2: 0.1214 😵 Target 3: 0.1226 😵 Target 4: 0.1238 😵 Target 5: 0.1250 😵 Target 6: 0.1273  '
        tps = re.findall(r'Target\s*\d+:\s*([\d\.]+)', pxd['tp'])
# tps = ['0.1202', '0.1214', '0.1226', '0.1238', '0.1250', '0.1273']
        return (pxd, tps)

#--------->-----------------------------------------------------------------
# "Coin #ASTER/USDT   Position: LONG   Leverage:  Cross25X  Entries: 2.04 - 1.99  Targets: 🎯 2.09, 2.14, 2.19 2.24, 2.29  Stop Loss: 1.94📌📌📌📌"
    def parse_2():

        pattern = (
            r'Coin\s*#(?P<sym>\w+/\w+)\s+'
            r'Position:\s*(?P<side>LONG|SHORT)\s+'
            r'Leverage:\s*(?P<leverage_type>\w+)(?P<leverage>\d+)X\s+'
            r'Entries:\s*(?P<entry1>[\d\.]+)\s*-\s*(?P<entry2>[\d\.]+)\s+'
            r'Targets:\s*🎯\s*(?P<tp>[\d\.,\s]+)\s+'
            r'Stop\s*Loss:\s*(?P<stloss>[\d\.]+)'
        )

        (px, pxd) = P.comp_line(pattern, atext)
        print("pattern= ", pxd)

        if len(px) != 8:
            return (None,None)

# pxd['tp'] ='2.09, 2.14, 2.19 2.24, 2.29 '
        tps = re.findall(r'[\d\.]+', pxd['tp'] )
# tps = ['0.1202', '0.1214', '0.1226', '0.1238', '0.1250', '0.1273']
        return (pxd, tps)


#==============================================================================
    rc = M.Order_Info()

    if len( p1 := P.proc_line("Coin : #", atext) ) == 0:
        pxd, tps = parse_1()

    elif len( p1 := P.proc_line("Position:", atext) ) == 0:
        pxd, tps = parse_2()
    else:
        print( "not a signal message" )
        return rc

    if pxd is None:
        print( "not a signal message" )
        return rc

    pprint( pxd )

    # rc.utc_now: dt = None
    # rc.entry_utc_timestamp: int = 0

    rc.symbol = pxd['sym'] #'BTC/USDT'

    rc.setOrderAct( pxd['side'] )  # 'Buy'/'Sell' Long/Short

    rc.setOrderType('market')   # market/limit/info
    rc.setOrderSide("open")     # open-1 / close-2

    rc.entry_leverage = int( pxd['leverage'] )   # multipluer

    e_price1 = float( pxd['entry1'] )
    e_price2 = float( pxd['entry2'] )
    rc.entry_price = [e_price1, e_price2]  # price_min, price_max

    rc.entry_base_size = 100  # usdt before leverage
    #rc.entry_coin_size = 0.33  # BTC

    rc.slPrice[0] = float( pxd['stloss'] )

    num = len( tps )
    if num >= 1:

        match num:
            case 1:
                proc_t = [100]
            case 2:
                proc_t = [50, 50]
            case 3:
                proc_t = [30, 50, 20]
            case 4:
                proc_t = [25, 35, 25, 15]
            case 5:
                proc_t = [20, 20, 30, 20, 10]
            case 6:
                proc_t = [20, 20, 30, 20, 5, 5]

            case _:
                sum1 = 0
                proc_t = []

                for i in range(0, num-1):
                    part = int(100/(num-i))
                    proc_t.append( part )
                    sum1 += part
                proc_t.append( 100-sum1 )

        rc.tpPrice = []
        for i in range(0, num):
            price = float( tps[i] )
            part = proc_t[i]
            rc.tpPrice.append( [price, part] )

    rc.entry_leverage_type = 0  # cross(0)/isoleited(1)

    rc.status = M.OrderStatus.Created
    return rc
