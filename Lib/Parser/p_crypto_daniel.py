
import traceback
import p_common as P, TMessage as M

DF = '(\d+.\d*)' # to parse 45 or 45.78

channel_name = "Crypto Daniel"
def parser(monitor, msg ):

    # the msg is not empty and msg.date has been checked
    text = ""
    try:
        if monitor.section_cfg.get("UserId",0 ) == 0 or monitor.section_cfg["UserId"] == msg.from_user.id:

            parser_msg = M.Order_Info()

            text = P.msg_text(msg)

            if text_parser( monitor, text, parser_msg) == 0:
                monitor.logInfo(f"+++++++ Channel {msg.chat.title}: Message is accepted: {text:.30}")
                return parser_msg

    except Exception as e:
        monitor.logError(f"Unexpected parser exception {e=}, {type(e)=}")
        monitor.logError( text )
        monitor.logError( traceback.format_exc(2, chain=True) )

    monitor.logError(f"Channel {msg.chat.title}: Message is skipped: {text:.30}")
    return None


def text_parser( monitor, text, rc_msg ):

    p1 = P.proc_line("\s*(\w+/USDT) (\w+)", text)

    if len(p1) == 2:

        rc_msg.setOrderSide("open")
        rc_msg.setOrderType('market')

        rc_msg.symbol = p1[0]
        rc_msg.setDirection(p1[1])

        p2 = P.proc_line("Вход: (\w+ \w+)", text)

        p3 = P.proc_line("Усреднение:\s*(\d+.\d+)", text)
        rc_msg.entry_price = [0, float(p3[0])]  # усреднее

        rc_msg.entry_leverage = 500  # плечо
        rc_msg.entry_volume = 100.0

        p4 = P.proc_line("Цели:\s*(\d+.\d+)(\s*(\d+.\d+)|)(\s*(\d+.\d+)|)(\s*(\d+.\d+)|)", text)
        rc_msg.tpPrice = [float(p4[i]) for i in range(0, 7, 2) if p4[i] is not None]

        p5 = P.proc_line("Стоп:\s*(\d+.\d+)", text)
        if p5[0] is not None:
            rc_msg.slPrice[0] = float(p5[0])

        return 0

    return 1