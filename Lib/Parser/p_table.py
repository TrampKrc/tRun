
import p_template

import p_crypto_daniel
import p_master_trade


parser_table = {

    p_crypto_daniel.channel_name : p_crypto_daniel.parser,
    p_master_trade.channel_name :  p_master_trade.parser,

    p_template.channel_name : p_template.parser

}