
import p_sample, p_xstars, p_timofey, p_crypto_pump_club

parser_table = {

    'XStars'                    : p_xstars.parser,
    'Канал Тимофея'             : p_timofey.parser,
    'Crypto Pump Club Official' : p_crypto_pump_club.parser,

    'Sig1' :        p_sample.parser,
    'Sig2' :        p_sample.parser,
    'EmptyParser' : p_sample.empty_parser
}
