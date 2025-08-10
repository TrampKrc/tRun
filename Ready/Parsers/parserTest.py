import appcfg as acfg
import tools as T

import p_common as P


# Crypto Daniel
from p_crypto_daniel import text_parser as parser

text = \
    """
APT/USDT LONG
Вход: по рынку
Усреднение:  4.9355

Цели: 5.2852   5.4307   5.9879

Стоп:  4.6215

Риск менеджмент:
Убыток по стопу не должен быть более 3% вашего депозита
    """


textW = \
    """

    """

textQ = \
    """

    """


if __name__ == '__main__':

    cfg_test = {
        'CfgFolder': acfg.cfg_files,
        'OutFolder': "UnDef-",

        "Section": {
            'CfgFolder': acfg.cfg_files,
            'OutFolder': "UnDef-"
        }
    }

    jclass = T.CfgJson( cfg_mem=cfg_test, section="Section")
    parser_msg = P.ParserMsg()

    jclass.logInfo(f"Text: {text}")

    if parser( jclass, text, parser_msg ) == 0:
        jclass.logInfo(f"Have Signal: {parser_msg=}", parser_msg)
    else:
        jclass.logInfo(f"No Signal")


