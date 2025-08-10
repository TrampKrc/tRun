
if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Lib')))
    import config as cfg            

#print( sys.path )
from colorPrint import colorPrint as clp


def test_1():
    clp.p_blue("Hello from test_1 in test_colorPrint.py")
    clp.p_green("This is a green message.")
    clp.p_red("This is a red message.")
    clp.p_yellow("This is a yellow message.")
    clp.p_cyan("This is a cyan message.")
    clp.p_magenta("This is a magenta message.") 

if __name__ == "__main__":
    test_1()