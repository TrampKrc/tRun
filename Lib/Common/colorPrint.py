import io
from pprint import pprint

class colorPrint( object ):
    red    = "\033[91m"
    green  = "\033[92m"
    green2 = "\033[38;5;155m"
    yellow = "\033[93m"
    blue   = "\033[94m"
    pink   = "\033[95m"
    cyan   = "\033[38;5;50m"
    magenta= "\033[38;5;201m"
    bold   = "\033[1m"    # reset '\033[22m'
    italic = "\033[3m"    # reset '\033[23m'
    underline = "\033[4m" # reset '\033[24m'
    reset  = "\033[0m"

    @classmethod
    def getSpec( cls, spec ) -> str:
        match spec:
            case    'red':
                return cls.red
            case 'green':
                return cls.green
            case 'green2':
                return cls.green2
            case 'yellow':
                return cls.yellow
            case   'blue':
                return cls.blue
            case  'pink':
                return cls.pink
            case  'cyan':
                return cls.cyan
            case 'magenta':
                return cls.magenta
            case 'bold':
                return cls.bold
            case 'italic':
                return cls.italic
            case 'underline':
                return cls.underline
            case 'reset':
                return cls.reset
            case _:
                return ""

    @classmethod
    def make_str(cls, *args, **kwargs) -> str:
        type = 'short' if kwargs.get( 'long', None) is None else 'long'
        return argStr( type, *args )

    @classmethod
    def row_print(cls, spec, buf ):
        print( spec, buf, cls.reset )
        #print( spec + buf + color.reset )

    @classmethod
    def s_print(cls, spec, *args, **kwargs):
        cls.row_print( spec, cls.make_str( *args, **kwargs) )

    @classmethod
    def t_print( cls, spec_text, *args, **kwargs):
        kwargs[ 'text' ] = 'aaaa'
        cls.s_print( cls.getSpec( spec_text ), *args, **kwargs)

    @classmethod
    def b_print( cls, spec_text, *args, **kwargs):
        cls.s_print( cls.getSpec( spec_text ) + cls.bold, *args, **kwargs)

    @classmethod
    def i_print( cls, spec_text, *args, **kwargs):
        cls.s_print( cls.getSpec( spec_text ) + cls.italic, *args, **kwargs)

    @classmethod
    def p_green(cls, *args, **kwargs):
        cls.s_print( cls.green,*args, **kwargs)

    @classmethod
    def p_blue( cls, *args, **kwargs):
        cls.s_print( cls.blue,*args, **kwargs)

    @classmethod
    def p_red( cls, *args, **kwargs):
        cls.s_print(cls.red, *args, **kwargs)

    @classmethod
    def p_yellow( cls, *args, **kwargs):
        cls.s_print(cls.yellow, *args, **kwargs)

    @classmethod
    def p_cyan( cls, *args, **kwargs):
        cls.s_print(cls.cyan, *args, **kwargs)

    @classmethod
    def p_magenta( cls, *args, **kwargs):
        cls.s_print(cls.magenta, *args, **kwargs)


def argStr( type, *args):
    if type == 'short':
        return ' '.join([ str(arg)    for arg in args if arg is not None])
    else:
        buf = io.StringIO()
        for arg in args:
            pprint( arg, stream=buf, compact=True, width=80)
        v_str = buf.getvalue()[:-1]  # remove last newline
        buf.close()
        return v_str


if __name__ == '__main__':
#    test_1()

    cfg_default = {
        'CfgFolder': "C:\\A",
        'OutFolder' : "UnDef-",

        "Section": {
            'CfgFolder': "D:/SS",
            'OutFolder': "UnDef-"
        }
    }

    colorPrint.t_print( 'red', ' red Hello, World!', cfg_default, '<--', long=90 )
    colorPrint.t_print('', 'Morning, World!', cfg_default, '<--')
    colorPrint.b_print('', 'Morning, World!', cfg_default, '<--')
    colorPrint.i_print('cyan', 'Morning, World!', cfg_default, '<--')

    colorPrint.s_print( colorPrint.pink, 'pink, Hello, World!', cfg_default, '<--' )

    colorPrint.p_green( 'Morning, World!', cfg_default, '<--' )
    colorPrint.p_blue( 'Morning, World!', cfg_default, '<--', long=1 )

