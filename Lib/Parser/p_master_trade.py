
import re
from datetime import timezone
import traceback
from pyrogram.errors.exceptions.all import exceptions

import p_common as P, TMessage as M

D = '(\d+.\d*)' # to parse 45 or 45.78

channel_name = "Мастерство трейдинга"
def parser(monitor, msg ):
    # the msg is not empty and msg.date has been checked

    text = ""
    try:
        if monitor.section_cfg.get("UserId", 0) == 0 or monitor.section_cfg["UserId"] == msg.from_user.id:

            parser_msg = M.Order_Info()
            text = P.msg_text(msg)

            if text_parser(monitor, text, parser_msg) == 0:
                return parser_msg

    except Exception as e:
        monitor.logError(f"Unexpected parser exception {e=}, {type(e)=}")
        monitor.logError(text)
        monitor.logError(traceback.format_exc(2, chain=True))

    monitor.logError(f"Channel {msg.chat.title}:  message is skipped: {text:.30}")
    return None

def text_parser(monitor, text, rc_msg):

        p1 = P.proc_line(f"\s*(\w+/USDT) в (\w+)!.+по рынку: {D}-{D}", text)

        if len(p1) == 4:

            rc_msg.setOrderSide( "open" )
            rc_msg.setOrderType( 'market' )

            rc_msg.symbol = p1[0]
            rc_msg.setDirection( p1[1] )

            rc_msg.comment = f'open range: {float( p1[2] )} {float( p1[3]) }'
            rc_msg.entry_price = [ float( p1[2] ), float( p1[3] ) ]  # range

            p2 = P.proc_line(f"Усреднение: {D}.+маржа (\d+)[xХ].+Стоп:\s*({D}|)", text, re.IGNORECASE)
            rc_msg.entry_price.append( float( p2[0] ))  # усреднее
            rc_msg.entry_leverage = int( p2[1] )        # плечо

            if p2[2] is not None:
                tmp = 0 if p2[2] == '' else p2[2]
                rc_msg.slPrice = [ float(tmp), 1 ] # size 100%
            else:
                rc_msg.slPrice = [ 0, 1 ]

            p3 = P.proc_line(f"Тейки: {D}, {D}, {D}", text)
            pos = [0.3, 0.5, 0.2]
            rc_msg.tpPrice = [ [float( p3[i] ), pos[i] ] for i in range(3) if p3[i] is not None ]

            p4 = P.proc_line("сделку на (\d+)\$", text)
            if p4[0] is not None:
                rc_msg.entry_volume = float( p4[0] )
            else:
                rc_msg.entry_volume = 100.0 # USDT

            # check stop loos price:
            # profit = s*l * ( p1 - p0 ) / p0
            # p1 = p0 + p0*pf/v;  stop_loss_price = p0 * ( 1 - loss_vol / size * leverage )
            # loss_vol  = size
            # stop_loss_price = p0 * ( 1 - 1/leverage )

            if rc_msg.slPrice[0] == 0:
                rc_msg.slPrice[0] = rc_msg.entry_price[0] * ( 1 - 1/rc_msg.entry_leverage)

            return 0

        return 1 # error


