
import re
from datetime import datetime as dt, timezone

class ParserMsgT( object ):

    def __str__(self):
        return self.str()

    def str(self):
        return (f'ParserMsg: utc= {self._utctime}\nchannel={self._channel};\n'
                f'channel date= {self._channel_time}\n'
                f'symbol={self.symbol}   side={self.side}  dir={self.direction}\n'
                f'open={self.openPrice}  size={self.size} leverage={self.leverage}\n'
                f'TP={self.tpPrice}  SL={self.slPrice}\n'
                f'note={self.note}')

    def __init__(self, msg = None ):
        self._type = type
        self._utctime = dt.now().astimezone(timezone.utc)

        if msg is not None:
            self._channel = msg.chat.title
            self._channel_time = msg.date
            self._channel_utctime = msg.date.astimezone(timezone.utc)
            self._channel_msgId = msg.id
        else:
            self._channel = "Unknown"
            self._channel_time = dt.now()
            self._channel_utctime = dt.now().astimezone(timezone.utc)
            self._channel_msgId = 0

        self._channel_timestamp = ""

        self._sessionId = ""
        self._session_msgId = ""
        self.note = ""

        self.symbol = ""    # NEAR/USDT
        self.side   = 1  # open-1 / close-2
        self.direction = 0  # buy / sell
        self.type = "Market"
        self.size = 0
        self.leverage = 0
        self.openPrice = [0]
        self.tpPrice = [0]
        self.slPrice = [0,0]

    def getDirection(self):
        return 'buy' if self.direction == 1 else 'sell'
    
    def setDirection(self, direction: str ):
        act = direction.lower()
        if act in ['buy', 'long']:
            self.direction = 1
        elif act in ['sell', 'short']:
            self.direction = 2
        else: self.side = 0

    def is_buy(self):
        return self.direction == 1


def proc_line(mask, line, flag=0):
    rcg = re.search(mask, line, flag)
    # if rcg and (data := rcg.groups()):
    return rcg.groups() if rcg else [None, None, None]

def comp_line(mask, line, flag=0):
    comp = re.compile(mask, flag)
    rcg = comp.search( line, flag)

    return (rcg.groups(), rcg.groupdict() ) if rcg else ([], {})


def proc_lines(mask, lines, end_mask, m, flag=0):
    gr = None
    for line in lines:
        m[0] += 1
        gr = proc_line(mask, line, flag)
        if gr[1]: break
        if end_mask in line:
            m[0] -= 1
            break

    return gr

def msg_text( msg ):
    text = "" if msg.caption == None else msg.caption
    text += "" if msg.text == None else msg.text
    text = "".join(text).replace("\n", " ")
    return text

"""
. (dot): Matches any character except newline
^: Start of string
$: End of string
*: Zero or more repetitions
+: One or more repetitions
?: Zero or one repetition, or makes preceding quantifier non-greedy
[]: Character set
(): Grouping
|: Alternation (OR)
\: Escape character
{}: Quantifier for specific number of repetitions
To match these characters literally, escape them with a backslash (\).

\s : Matches any whitespace character (space, tab, newline).
\S : Matches any non-whitespace character.
\w : Matches any word character (alphanumeric & underscore).
\W : Matches any non-word character.
\d : Matches any digit (0-9).
\D : Matches any non-digit.
\b : Matches a word boundary.
\B : Matches a non-word boundary.
\A : Matches the start of the string.
\Z : Matches the end of the string.
\n : Matches a newline.
\t : Matches a tab.
\\ : Matches a literal backslash.

"""