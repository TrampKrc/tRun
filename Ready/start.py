#from ..lib import *
#import clp
#import Lib.Common.colorPrint


#import Lib.Common.colorPrint as clp
#from Lib.Common.colorPrint import colorPrint as clp

print( "call: ", __name__, __file__ )

def start_1():
    print( "test 1 ", __name__)

    clp.p_blue( "Hello from Ready.start_1" )

if __name__ == '__main__':

    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Lib')))

    import config as cfg
    
    #asyncio.run( telegram_main() )
    start_1()
