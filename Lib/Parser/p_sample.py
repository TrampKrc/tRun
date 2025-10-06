
import traceback
import p_common as P, TMessage as M
from pprint import pprint

DF = '(\d+.\d*)' # to parse 45 or 45.78

channel_name = "SampleParser"
def parser(monitor, telegram_msg ):

    telegram_msg_text = P.msg_text( telegram_msg )
    try:
        # the msg is not empty and msg.date has been checked
        if (monitor.cfg_section.get("UserId", 0) == 0 or
            monitor.cfg_section["UserId"] == telegram_msg.from_user.id):

            order_data = text_parser(monitor, telegram_msg_text )
            if order_data:
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

def text_parser( monitor, text ) -> M.Order_Info:

    rc = M.Order_Info()
    # rc.utc_now: dt = None
    # rc.entry_utc_timestamp: int = 0

    pattern = (
        r'(?P<sym>\w+/\w+)\s+'
        r'(?P<side>Buy|Sell)\s+'
        r'lev:\s*(?P<leverage>\d+)\s+'
        r'usdt:\s*(?P<usdt>\d*.\d*)\s+'
        r'sL:\s*(?P<stloss>\d*.\d*)\s+'
        r'tP:\s*(?P<tp>[\d*.\d*\s,]*)'
    )

    (px, pxd) = P.comp_line( pattern, text)

    #pprint( text )
    print( "pattern= ",pxd )

    if len(px) != 6:
        return rc

    rc.symbol = pxd['sym']  #'BTC/USDT'

    rc.setOrderAct( pxd['side'] )  # 'Buy' / 'Sell' Long/Short

    rc.setOrderType('market')   # market/limit/info
    rc.setOrderSide("open") # open-1 / close-2

    rc.entry_leverage = int( pxd['leverage'] )   # multipluer
    rc.entry_base_size = float( pxd['usdt'] )  # usdt before leverage
    #rc.entry_coin_size = 0.33  # BTC

    rc.slPrice[0] = float( pxd['stloss'] )

    tps = pxd['tp'].split(',')
    num = len( tps )
    if num >= 2:
        rc.tpPrice = []
        for i in range(0, num, 2):
            price = float( tps[i] )
            part = float( tps[i+1] )
            rc.tpPrice.append( [price, part] )

    #rc.entry_price = [300.0, 400.0]  # price_min, price_max
    # rc.entry_leverage_type: int = 0  # cross(0)/isoleited(1)

    rc.status = M.OrderStatus.Created
    return rc

def empty_parser(monitor, telegram_msg ):
    monitor.logError(f"parser for Channel '{telegram_msg.chat.title}' is not implemented")
    return None
