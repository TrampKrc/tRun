
import os, sys
import logging, json
from pprint import pprint
from datetime import datetime as dt, timezone, timedelta
from time import localtime, strftime

from colorPrint import colorPrint as cp
import config as acfg
#root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(root + '/python')

#V2Dir = os.path.dirname( os.path.dirname(os.path.abspath(__file__)) )
#FilePath = V2Dir + '/Files/'

#folder0 = os.path.dirname(os.path.abspath(__file__))
#folder_up1 = os.path.dirname(folder0)
#sys.path.append( V2Dir + '/Tools')

PrjFolder=acfg.main_folder
CfgFolder= acfg.cfg_files

cfg_default = {
    'CfgFolder': acfg.cfg_files,
    'OutFolder' : "UnDef-",

    "Section": {
        'CfgFolder': acfg.cfg_files,
        'OutFolder': "UnDef-"
    }
}

class CfgJson(object):
    _cfg_all: dict
    is_running: bool

    def __init__(self, cfg_file=None, section=None, cfg_mem=None, lname='Logger', prefix='Loger' ) -> None:

        self.prefix = prefix

        self._cfg_all = cfg_default
        self._cfg_section = None

        if cfg_file is not None:
            if os.path.exists( cfg_file ):
                self._cfg_all = read_json( cfg_file )
            else:
                st = f"Nof found cfg file: {cfg_file} "
                raise ValueError( st )

        elif cfg_mem is not None:
            self._cfg_all = cfg_mem

        else:
            raise ValueError("No cfg_file neither cfg ")

        if section is not None:
            if self.cfg_all.get(section, None) is not None:
                self._cfg_section = self.cfg_all.get(section)
            else:
                raise ValueError( f"CfgJson: parameter section = {section} is not found")
        else:
            self._cfg_section = self.cfg_all

        self.cfg_folder = self._cfg_section.get("CfgFiles", self.cfg_all.get( "CfgFiles", acfg.cfg_files ))
        self.out_folder = self._cfg_section.get("OutFiles", self.cfg_all.get( "OutFiles", acfg.out_files ))

        self.log_file = self._cfg_section.get("LogFile", self.cfg_all.get( "LogFile", None ))

        if self.log_file:
            self.filename = os.path.join( self.out_folder, self.log_file + strftime("%m%d%Y-%H%M%S.log", localtime()) )
            logging.basicConfig(
                filename=self.filename, encoding='utf-8', filemode='w', format='%(asctime)s %(message)s',
                datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)  ##DEBUG)

            self.log = logging.getLogger( 'Logger' )
            self.logInfo(f"Open LogFile: {self.filename}", c=cp.green2 )

    @property
    def cfg_all(self):
        return self._cfg_all

    @property
    def cfg_section(self):
        return self._cfg_section
    
    def _to_screen(self, level, *args, **kwargs):
        st = f"{dt.now()}  {self.prefix} {level}" + cp.make_str( *args, **kwargs)

        if kwargs.get( 'file_only', None) is None:
            spec = kwargs.get( 'c', cp.getSpec(kwargs.get('cl', '') ))
            cp.row_print( spec, st)
        return st

    def cprint(self, spec, *args, **kwargs):
        st = f"{dt.now()}  {self.prefix} " + cp.make_str( *args, **kwargs)
        cp.row_print( spec, st )

    def logInfo(self, *args, **kwargs):
        st = self._to_screen( 'Info: ', *args, **kwargs)
        if self.log_file:  self.log.info( st )

    def logError(self, *args, **kwargs):
        kwargs['long'] = 1
        kwargs['c'] = cp.red + cp.bold
        st = self._to_screen( 'Error: ', *args, **kwargs)
        if self.log_file:  self.log.error( st )

    def logDebug(self, *args, **kwargs):
        kwargs['long'] = 1
        kwargs['c'] = cp.yellow
        st = self._to_screen( 'Debug: ', *args, **kwargs)
        if self.log_file:  self.log.debug(st)

    def logException(self, *args, **kwargs):
        st = self._to_screen( 'Exception: ', *args, **kwargs)
        if self.log_file:  self.log.exception(st)

class CfgAPI( object ):
    def __init__(self, cfg_log_class ):
        self.cl_class = cfg_log_class

    def __getattr__(self, name):
        return getattr( self.cl_class, name )

    @property
    def base(self):
        return self.cl_class

    @property
    def cfg_all(self):
        return self.base.cfg_all

    @property
    def cfg_section(self):
        return self.base.cfg_section

    def cprint(self, spec, *args, **kwargs):
        return self.base.cprint( spec, *args, **kwargs)

    def print_r(self, *args, **kwargs):
        return self.base.cprint( cp.red, *args, **kwargs )

    def print_g(self, *args, **kwargs):
        return self.base.cprint( cp.green, *args, **kwargs )

    def print_b(self, *args, **kwargs):
        return self.base.cprint( cp.blue, *args, **kwargs )

    def print_y(self, *args, **kwargs):
        return self.base.cprint( cp.yellow, *args, **kwargs )

    def logInfo(self, *args, **kwargs):
        self.base.logInfo( *args, **kwargs)

    def logError(self, *args, **kwargs):
        self.base.logError( *args, **kwargs)

    def logDebug(self, *args, **kwargs):
        self.base.logDebug( *args, **kwargs)

    def logException(self, *args, **kwargs):
        self.base.logException( *args, **kwargs)


class mash(object):
    def __init__(self, data={}):
        data = { k:self.pack(v) for k,v in dict(data).items() }
        super(mash, self).__setattr__('_dict_instance', data)

    @classmethod
    def pack(cls, obj):
        if isinstance(obj, dict):
            return mash(obj)
        elif isinstance(obj, list):
            return map(lambda it: cls.pack(it), obj)
        elif isinstance(obj, tuple):
            return cls.pack(list(obj))
        return obj

    @classmethod
    def unpack(cls, obj):
        if isinstance(obj, mash):
            return {k:cls.unpack(v) for k,v in dict(obj._dict_instance).items()}
        elif isinstance(obj, list):
            return map(lambda it: cls.unpack(it), obj)
        elif isinstance(obj, tuple):
            return cls.unpack(list(obj))
        return obj

    def __getitem__(self, name):
        return self._dict_instance.get( name )
    #return self._dict_instance[name]

    def __setitem__(self, name, value):
        self._dict_instance[name] = self.pack(value)

    def __delitem__(self, name):
        del self._dict_instance[name]

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    def __contains__(self, item):
        return item in self._dict_instance

    def __iter__(self):
        for k, v in self._dict_instance.iteritems():
            yield (k, self.unpack(v))

    def __str__(self):
        return 'mash:' + self._dict_instance.__str__()

    def __repr__(self):
        return 'mash(' + self._dict_instance.__repr__() + ')'

    def __sizeof__(self):
        len( self._dict_instance )

    @classmethod
    def fromdict(cls, data={}):
        obj = mash.__new__(cls)
        super(cls, obj).__init__(data)
        return obj

    @property
    def asdict(self):
        return self.unpack(self)
#================================================



def argStr(*args):
    return ' '.join([str(arg) for arg in args])

# print a colored string
def dump(*args):
    print( argStr(*args) )

# print an error string
def dump_error(*args):
    string = argStr(*args)
    print(string)
    sys.stderr.write(string + "\n")
    sys.stderr.flush()

def read_json( fn_name ):
    with open( fn_name, 'rb') as f:
        try:
          return json.load( f )
        except:
          raise Exception('json file %s is invalid:\n%s' % ( fn_name, sys.exc_info()[1])  )

def read_json2( fn_name ):

    def encode_to_ascii(data):
        ascii_encode = lambda x: x.encode('ascii') if isinstance(x, str ) else x
        return dict( map( ascii_encode, pair ) for pair in data.items() )

    with open( fn_name, 'r') as f:
        try:
            return json.load( f, object_hook=encode_to_ascii )
        except:
            raise Exception('json file %s is invalid:\n%s' % ( fn_name, sys.exc_info()[1])  )


def read_json3( fn_name ):
    def m_code( x ):
        #if isinstance(x, unicode):
        if isinstance(x, str ):
            return x.encode('ascii')
        elif isinstance(x, list):
            return map( m_code, x )
        else:
            return x

    def encode_to_ascii(data):
        return dict( map( m_code, pair ) for pair in data.items() )

    with open( fn_name, 'rb') as f:
        try:
            return json.load( f, object_hook=encode_to_ascii )
        except:
            raise Exception('json file %s is invalid:\n%s' % ( fn_name, sys.exc_info()[1])  )

def save_to_json( file, data ):

   if file and data :
        with open( file, 'w', encoding='utf-8') as f:
            json.dump( data, f, sort_keys=False, indent=4, ensure_ascii=False )
            #ss = json.dumps( data, sort_keys=False, indent=4)
            #f.write( json.dumps( data, sort_keys=False, indent=4))
        return 0

   else:
        print( "Can not store data in json format. Processing failed!" )
        return 1

def LocalTimeZone():
    now = dt.now()
    local_tz = now.astimezone().tzinfo
    return local_tz.tzname(now), local_tz.utcoffset( now ).total_seconds()//3600

#    dt.astimezone().strftime('%Y-%m-%d %H:%M:%S%z (%Z)')

def LocalWithTimeZone( date: dt ):
    local_tz = dt.now().astimezone().tzinfo
    return date.astimezone( local_tz )


def Iso2LocalDate( date_iso ):       # '2024-04-12 23:00:00-07:00')
    local_tz = dt.now().astimezone().tzinfo
    dd = dt.fromisoformat(date_iso)

    return  dd.astimezone(local_tz) # '2024-04-13 00:00:00-06:00')  -06 local zone

def Iso2UtcDate( date_iso ):              # '2024-04-12 23:00:00-07:00')
    dd = dt.fromisoformat(date_iso)
    return dd.astimezone( timezone.utc ) # '2024-04-13 06:00:00+00:00')  UTC

def ISO2UTCDateT( date_iso ):

    local_tz = dt.now().astimezone().tzinfo
    dd = dt.fromisoformat('2024-04-12 23:00:00-07:00')
    dd2 = dd.astimezone( local_tz )
    utc = dd.astimezone( timezone.utc )
    #str1 = dd2.strftime('%Y-%m-%d %H:%M:%S')
    print( dd, dd2, utc )

def Iso2UtcTimeStamp( date_iso ):
    return Iso2UtcDate( date_iso ).timestamp()

def utctimeStamp2Zone( UTCstamp, hours=0, mins=0):
    offset = timedelta(hours=hours, minutes=mins)
    utc2 = timezone( offset )
    return dt.fromtimestamp( UTCstamp, timezone.utc).astimezone( utc2 )

def UtcTimeStamp2Date( UTCstamp, format="%Y-%m-%d %H:%M:%S:%:z", hours=0, mins=0):
    zone_date = utctimeStamp2Zone( UTCstamp, hours, mins)
#    sign = "-" if hours < 0 else "+"
#    zone = "" if hours == 0 else "{}:{:2d}:{:2d}".format( sign, hours, mins)
    return zone_date.strftime( format ) # + zone
    #return utc.astimezone( timezone.utc )

def UtcTimeStampMiliSec2Date( UTCstamp, format="%Y-%m-%d %H:%M:%S.$f", hours=0, mins=0 ):
    zone_date = utctimeStamp2Zone( UTCstamp // 1000, hours, mins)
    sign = "-" if hours < 0 else "+"
    return zone_date.strftime(format)[:-6] + "{:03d}:%s{:02d}:{:02d}".format(int( UTCstamp) % 1000, sign, hours, mins  )
    #return zone_date.strftime(format)[:-6] + "{:03d}:{:02d}:{:02d}".format(int( UTCstamp) % 1000, hours, mins  )
    #return utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-6] + "{:03d}".format(int(timestamp) % 1000) + 'Z'



def test_1():

    #jdata = CfgJson(cfg_file=path + "cfg-h1.json", section="ChannelH1")  # ,cfg=None )
    jdata = CfgJson( cfg = cfg_default )

    print( "===================")
    jdata.log.info( '12' ) #, "qaz")
    #jdata.log.info( '14', "qaz")

    print("=================== SECOND =====")
    jdata.logInfo( 10, "wsw", jdata.__dict__ )
    jdata.logInfo( 'green', c=cp.green2)


if __name__ == '__main__':
#    test_1()

    jdata = CfgJson( cfg_mem = cfg_default )

    pprint( jdata )

    jdata.logInfo( 'No color 1', 'No color 2!' ) #, file_only=True )
    jdata.logInfo( 'red', 'Hello, World!', c=cp.red ) #, file_only=True )
    jdata.logInfo(  'green', 'Hello, World!', c=cp.bold+cp.italic)

    cp.p_blue( 'Hello, World!\n' )
    jdata.cprint( cp.yellow + cp.bold, 'Hello, World!' )