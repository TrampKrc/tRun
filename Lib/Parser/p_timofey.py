
import traceback
import p_common as P, TMessage as M
from pprint import pprint

from TMessage import OrderStatus

DF = '(\d+.\d*)' # to parse 45 or 45.78

channel_name = "Канал Тимофея"
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

    rc = M.Order_Info()

    if len( p1 := P.proc_line("Тимофеевский сигнал", atext) ) != 0:
        print( "not a signal message" )
        return rc

    # rc.utc_now: dt = None
    # rc.entry_utc_timestamp: int = 0

#' Тимофеевский сигнал 👏👍   пара - LTC/USDT  направление - шорт плечо - 30 кросс цена входа - 119.54 стоп - 128.14 цели - 115,65 / 111,17 / 107,03 / 104,29  Всем подписчикам выдаю вип-статусы на 👉 WEEX (жми) 👈 '

    pattern = (
        r'пара\s*-\s*(?P<sym>\w+/\w+)\s+'
        r'направление\s*-\s*(?P<side>\w+)\s+'
        r'плечо\s*-\s*(?P<leverage>\d+)\s+\w+\s+'
        r'цена входа\s*-\s*(?P<entry>[\d\.]+)\s+'
        r'стоп\s*-\s*(?P<stloss>[\d\.]+)\s+'
        r'цели\s*-\s*(?P<tp>[\d\.,\s/]+)'
    )

    (px, pxd) = P.comp_line( pattern, atext)
    print( "pattern= ",pxd )

    if len(px) != 6:
        return rc

    rc.symbol = pxd['sym'] #'BTC/USDT'

    rc.setOrderAct( pxd['side'] )  # 'Buy'/'Sell' Long/Short

    rc.setOrderType('market')   # market/limit/info
    rc.setOrderSide("open")     # open-1 / close-2

    rc.entry_leverage = int( pxd['leverage'] )   # multipluer

    e_price = float( pxd['entry'] )
    rc.entry_price = [e_price, e_price]  # price_min, price_max

    rc.entry_base_size = 100  # usdt before leverage
    #rc.entry_coin_size = 0.33  # BTC

    rc.slPrice[0] = float( pxd['stloss'] )

# pxd['tp'] ='115,65 / 111,17 / 107,03 / 104,29  '
    proc_t = [30, 50, 20 ]
    tps = pxd['tp'].strip().split('/')
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
                proc_t = [20, 30, 20, 20, 10]
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
            price = float( tps[i].replace(',', '.').strip() )
            part = proc_t[i]
            rc.tpPrice.append( [price, part] )

    rc.entry_leverage_type = 0  # cross(0)/isoleited(1)

    rc.status = M.OrderStatus.Created
    return rc
