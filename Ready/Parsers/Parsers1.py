
import re
from datetime import timezone
import traceback
from pyrogram.errors.exceptions.all import exceptions

import p_common as P, TMessage as M

D = '(\d+.\d*)' # to parse 45 or 45.78

def process_channel( monitor, msg ):

    monitor.logError(f"Channel {msg.chat.title} is not implemented ")

    text = " Init processing "
    try:
        #if monitor.section_cfg["UserId"] == 0 or monitor.section_cfg["UserId"] == msg.from_user.id:
        # text = P.msg_text(msg)
        pass

    except Exception as e:
        monitor.logError(f"Unexpected parser exception {e=}, {type(e)=}")
        monitor.logError( text )
        monitor.logError( traceback.format_exc(2, chain=True) )

    monitor.logError(f"Channel {msg.chat.title} is not implemented ")
    return None

def process_channel_S1( monitor, msg ):
    monitor.logError(f"Channel {msg.chat.title} is not implemented ")
    return None

def process_channel_Sig( monitor, msg ):

    text = P.msg_text( msg )

    #redirect to "name name name"
    to_ = P.proc_line("Redirect to:\s*\"(.*)\"", text)
    if to_[0] is not None:
        msg.chat.title = to_[0]
        monitor.logInfo( f"Handler YK_SIG1; redirect to {to_[0]}")
        return True
    else:
        monitor.logInfo( "Handler YK_SIG1; redirect not found")
        return False

def process_master_trading(monitor, msg ):

    # the msg is not empty and msg.date has been checked
    # if self.section_cfg["UserId"] in [0, msg.from_user.id ]:
    text = " Init processing "
    try:
        if monitor.section_cfg["UserId"] == 0 or monitor.section_cfg["UserId"] == msg.from_user.id:
    
            text = P.msg_text(msg)
            #if T.proc_line("(Открываю сделку)", text)[0] is not None:
    
            p1 = P.proc_line(f"\s*(\w+/USDT) в (\w+)!.+по рынку: {D}-{D}", text)
            if len(p1) == 4:
    
                rc = M.Order_Info()
    
                rc.setOrderSide( "open" )
                rc.setOrderType( 'market' )
                rc.symbol = p1[0]
                rc.setDirection( p1[1] )
    
                rc.comment = f'open range: {float( p1[2] )} {float( p1[3]) }'
                rc.entry_price = [ float( p1[2] ), float( p1[3] ) ]  # range
    
                p2 = P.proc_line(f"Усреднение: {D}.+маржа (\d+)[xХ].+Стоп:\s*({D}|)", text, re.IGNORECASE)
                rc.entry_price.append( float( p2[0] ))  # усреднее
                rc.leverage = int( p2[1] )        # плечо
    
                if p2[2] is not None:
                    tmp = '0' if p2[2] == '' else p2[2]
                    rc.slPrice = [ tmp ]
    
                p3 = P.proc_line(f"Тейки: {D}, {D}, {D}", text)
                pos = [25, 50, 25]
                rc.tpPrice = [ [float( p3[i] ), pos[i] ] for i in range(3) if p3[i] is not None ]
    
                p4 = P.proc_line("сделку на (\d+)\$", text)
                if p4[0] is not None:
                    rc.size = float( p4[0] )
    
                return rc
            
    except Exception as e:
        monitor.logError(f"Unexpected parser exception {e=}, {type(e)=}")
        monitor.logError( text )
        monitor.logError( traceback.format_exc(2, chain=True) )
    
    return None

def process_crypto_daniel(monitor, msg ):

    # the msg is not empty and msg.date has been checked
    # if self.section_cfg["UserId"] in [0, msg.from_user.id ]:
    if monitor.section_cfg["UserId"] == 0 or monitor.section_cfg["UserId"] == msg.from_user.id:

        text = P.msg_text(msg)

        p1 = P.proc_line("\s*(\w+/USDT) (\w+)", text)
        if len(p1) == 2:

            rc = P.ParserMsg(msg)
            rc.side = 1     # open
            rc.type = 'market'

            rc.symbol = p1[0]  # BTC/USDT
            rc.setDirection( p1[1] )

            p2 = P.proc_line("Вход: (\w+ \w+)", text)

            p3 = P.proc_line("Усреднение:\s*(\d+.\d+)", text)
            rc.openPrice = [0, float(p3[0]) ]  # усреднее

            rc.leverage = 500   # плечо

            p4 = P.proc_line("Цели:\s*(\d+.\d+)(\s*(\d+.\d+)|)(\s*(\d+.\d+)|)(\s*(\d+.\d+)|)", text)
            rc.tpPrice = [ float( p4[i] ) for i in range( 0,7,2 ) if p4[i] is not None ]

            p5 = P.proc_line("Стоп:\s*(\d+.\d+)", text)
            if p5[0] is not None:
                rc.slPrice[0] = float(p5[0])

            return rc

    return None

def process_cryptonec(monitor, msg ):

    # the msg is not empty and msg.date has been checked
    # if self.section_cfg["UserId"] in [0, msg.from_user.id ]:
    if monitor.section_cfg["UserId"] == 0 or monitor.section_cfg["UserId"] == msg.from_user.id:

        text = P.msg_text(msg)

        p1 = P.proc_line("\s*#(\w+)USDT (\w+)", text)
        if len(p1) == 2:

            rc = P.ParserMsg(msg)
            rc.side = 1     # open
            rc.type = 'market'

            rc.symbol = p1[0]+'/USDT'  # BTC/USDT
            rc.setDirection( p1[1] )

            p2 = P.proc_line(f"Вход: {D}.+Цель:\s*{D} \({D}%\).+Стоп:\s*{D} \({D}%\)", text)

            rc.openPrice = [0, float(p2[0]) ]  # enter

            rc.leverage = 500   # плечо

            rc.tpPrice = [ float( p2[1] ) ]
            if p2[3] is not None:
                rc.slPrice[0] = float(p2[3])

            return rc

    return None

def process_trade_indicator(monitor, msg ):
    # the msg is not empty and msg.date has been checked
    # if self.section_cfg["UserId"] in [0, msg.from_user.id ]:
    if monitor.section_cfg["UserId"] == 0 or monitor.section_cfg["UserId"] == msg.from_user.id:

        text = P.msg_text(msg)

        p1 = P.proc_line(f"\s*#(\w+/USDT)\s*- (\w+)", text)
        if len(p1) == 2:

            rc = P.ParserMsg(msg)
            rc.side = 1     # open
            rc.type = 'market'

            rc.symbol = p1[0]  # BTC/USDT
            rc.setDirection( p1[1] )

            p2 = P.proc_line(f"Открытие -{D}-{D}", text)
            rc.openPrice = [float(p2[0]), float(p2[1])]  # range

            p3 = P.proc_line(f"Цели - 1-{D} 2-{D} 3-{D} (4-{D}|)", text)
            rc.tpPrice = [ float( p3[i] ) for i in range( 3 ) if p3[i] is not None ]
            if p3[4] is not None: rc.tpPrice.append( float( p3[4] ) )

            p4 = P.proc_line(f"Плечо\s*-\s*х(\d+).+\s*Стоп\s*-\s*{D}", text)
            if p4[0] is not None:
                rc.leverage = int(p4[0]) # плечо

            if p4[1] is not None:
                rc.slPrice[0] = float(p4[1])

            return rc

    return None

def process_channel_cornix( monitor, msg ):
    
    import gMessage as M
    
    if monitor.channel_cfg["UserId"] == 0 or msg.from_user.id == monitor.channel_cfg["UserId"] :

        lines = msg.dice.splitlines()
        for line in lines[ 0 : min( 4, len(lines)) ]:

            # check line = "Futures transaction"
            if ( data := P.proc_line("(Futures transaction)", line)[0]) or \
               ( data := P.proc_line("(price is)", line)[0] ) or \
               ( data := P.proc_line("(can click)", line)[0] ):

                record = {"Direction": -1, "MsgId": 0, "TDate": "10", "UTCDate": "10", "Note": " ",
                          "ClosePrice": 0.0}

                qMsg = M.qMsg()

                record["MsgId"] = msg.id
                record["TDate"] = msg.date
                record["UTCDate"] = msg.date.astimezone(timezone.utc)  # T.Iso2UtcDate( msg.date )

                if 'Trade direction' in msg.dice:
                    if "Long" in msg.dice:
                        record['Direction'] = 1  # 1. open long / 2. open short / 3. close
                    else:
                        record['Direction'] = 2  # 1. open long / 2. open short / 3. close

                elif "can click" in msg.dice:
                    record['Direction'] = 3  # close
                    p = msg.dice.find("%")
                    if p > 0: record["Note"] = msg.dice[p - 3:p + 1]

                elif "price is" in msg.dice:
                    record['Direction'] = 3  # close
                    gs = P.proc_line("\s*(\d+.\d+)", msg.dice)
                    if gs[0] is not None: record["ClosePrice"] = gs[0]

                return qMsg
    return None

