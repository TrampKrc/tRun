
import traceback
import p_common as P, TMessage as M

DF = '(\d+.\d*)' # to parse 45 or 45.78

channel_name = "Template"
def parser(monitor, msg ):

    """
    text = " Init processing "
    try:
        # the msg is not empty and msg.date has been checked
        if monitor.section_cfg.get("UserId", 0) == 0 or monitor.section_cfg["UserId"] == msg.from_user.id:

            parser_msg = M.Order_Info()
            text = P.msg_text(msg)

            if text_parser(monitor, text, parser_msg) == 0:

                # additional processing of parser_msg

                return parser_msg

    except Exception as e:
        monitor.logError(f"Unexpected parser exception {e=}, {type(e)=}")
        monitor.logError( text )
        monitor.logError( traceback.format_exc(2, chain=True) )
    """

    monitor.logError(f"parser for Channel '{msg.chat.title}' is not implemented")
    return None


def text_parser( monitor, text, rc_msg ):

    #p1 = P.proc_line("\s*(\w+/USDT) (\w+)", text)
    return 0
