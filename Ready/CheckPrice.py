
from datetime import datetime
import traceback

from yk_bybit import yk_Bybit
#from binance_exchange import binance_Exchange

import tools as T
from tools import CfgJson

from sqliteSupport import Dbase

from dataclasses import dataclass


@dataclass
class pTarget:
    #def __init__(self, price, size=0, proc=0 ):
    # Defaults are used if not provided AND if __init__ is auto-generated or doesn't set them.

    price: float = 0.0
    size: float  = 0.0  # % of the original position, e.g. 25%
    proc: float  = 0.0  # % of profit / loss, e.g. 10% profit or -5% loss
    
    time_hit: int = 0
    profit: float = 0.0 # Calculated profit based on size and proc in USDT

    def __init__(self, price, size=0, proc=0 ):
        if price == 0.0:
            raise ValueError("pTarget:  price = 0 ")
        
        self.price = price
        self.size = size
        self.proc = proc if proc != 0.0 else 100.0

    @property
    def Hit(self) -> bool:
        return self.time_hit != 0
        
    def calculate(self, pos_price, vol=1000, buy=True):
        if pos_price == 0:
            # Avoid division by zero; decide how to handle this (e.g., raise error, set proc to 0 or specific value)
            self.proc = 0.0
            self.profit = 0.0
            # raise ValueError("pos_price cannot be zero for calculation.")
            return

        self.proc = ( self.price - pos_price if buy else pos_price - self.price ) * 100 / pos_price
        self.profit = (vol * self.size) / 100 * self.proc / 100


@dataclass
class OHLCV:
    D : datetime
    Ts: int
    O : float
    H : float
    L : float
    C : float
    V : float

    def __init__(self, p = None ):
        self._initialize_fields( p )

    def _initialize_fields( self, p: any=None ):
        if p is None:
            self.D = datetime.now()
            self.Ts = int( self.D.timestamp() )
            self.O = 0
            self.H = 0
            self.L = 0
            self.C = 0
            self.V = 0
            return

        type_p = type( p )
        if isinstance(p, list):
            self.D = datetime.fromtimestamp( p[0]//1000 )
            self.Ts = p[0]//1000
            self.O = p[1]
            self.H = p[2]
            self.L = p[3]
            self.C = p[4]
            self.V = p[5]

        elif isinstance(p, OHLCV):
            self.D = p.D
            self.Ts = p.Ts
            self.O = p.O
            self.H = p.H
            self.L = p.L
            self.C = p.C
            self.V = p.V
        else:
            raise TypeError(f"Not a valid type for OHLCV initialization: {type(p)}")

def test():
    p2 = pTarget( 200 )
    p3 = pTarget( 200, 10)
    p3 = pTarget( 200, proc = 10)
    j = 0
    #p2 = OHLCV()
    
#test()
#exit(0)
@dataclass
class TargetPriceChecker:
    jdata: T.CfgJson
    
    def __init__(self, jdata):
        self.jdata: T.CfgJson = jdata
        self._broker_ready: bool = False
        self._pair: str = None
        self._start_time: int = None

        try:
            self.broker = yk_Bybit('ByBit', jdata)
            self.broker.connect_pub()
            exchange = self.broker._exchange
            
            method = 'fetchOHLCV'
            # check for capability
            if exchange and hasattr(exchange, 'has') and isinstance(exchange.has, dict) and \
                    method in exchange.has and exchange.has[method]:
                self._broker_ready = True
                self.jdata.logInfo("TargetPriceChecker: Broker connected and fetchOHLCV is available.")
            else:
                # _broker_ready remains False
                self.jdata.logError(
                    f"TargetPriceChecker: Broker connected but '{method}' capability missing or 'has' attribute malformed.")
        
        except Exception as e:
            # _broker_ready remains False
            self.jdata.logError(f"TargetPriceChecker __init__ connection failed: {type(e).__name__} : {str(e)}")
            traceback.print_exc()  # Good for debugging
        
        if not self._broker_ready:
            self.jdata.logError("TargetPriceChecker: Broker not ready after connection attempt.")
    
    @property
    def isReady(self) -> bool:
        return self._broker_ready
    
    @property
    def Pair(self) -> str:
        return self._pair
    
    def setPair(self, pair: str):
        self._pair = pair.upper()
    
    @property
    def StartTime(self) -> int:
        return self._start_time
    
    def setStartTime(self, time_utc: int):
        self._start_time = time_utc
    
    def getPrice(self, frame: str = '5m', t_since_utc: int = 0, lim: int = 60):

        if not self.isReady:
            self.jdata.logError("getPrice: Broker not ready.")
            return None
        
        if not self.Pair:
            self.jdata.logError("getPrice: Pair not set.")
            return None

        ex_broker = self.broker._exchange
        ohlcvs = []
        try:
            # ohlcvs = exchange.fetchOHLCV('BTC/USDT', '5m', since=from_ts_utc, limit=10)
            # ohlcvs = await exchange.watch_ohlcv(symbol, timeframe, None, limit)
            
            ohlcvs = ex_broker.fetchOHLCV(self.Pair, frame, since=t_since_utc * 1000, limit=lim)
            now = ex_broker.milliseconds()
            self.jdata.logInfo(
                f"Loop iteration: current UTC time: {ex_broker.iso8601(now)} {self.Pair} {frame} {t_since_utc}")
            
            if ohlcvs:  # Check if data was fetched
                pass
                # Prepare data for the table function, ensuring consistent structure (list of lists)

                # self.jdata.logInfo("\n" + table(
                #    [[{'col1': 0, 'col2': 0}] + [[o[0] // 1000] + [ex_broker.iso8601(o[0])] + o[1:] for o in ohlcvs]]))
                # self.jdata.logInfo( "\n" + table([ [ o[0] // 1000 ] + [ T.UtcTimeStamp2Date( o[0]//1000 )] + o[1:] for o in ohlcvs]))
               
                #headers = ["Timestamp", "ISO8601", "Open", "High", "Low", "Close", "Volume"]
                #formatted_data_for_table = [headers] + \
                #                           [[o[0] // 1000] + [ex_broker.iso8601(o[0])] + o[1:] for o in ohlcvs]
                #self.jdata.logInfo("\n" + table(formatted_data_for_table))
            
        except Exception as e:
            self.jdata.logError(f"getPrice() error: {type(e).__name__} : {str(e)}")
            traceback.print_exc()  # Good for debugging
            return None  # Return None on error
        
        if len(ohlcvs) != 0:
            data_list = [OHLCV(x) for x in ohlcvs]
            return data_list
        
        return None
    
    # check if real price hit target price
    def hitChecker(self, ts_start_utc, limit, take_profit, stop_loss):
        if not self.isReady:
            self.jdata.logError("hitChecker: Broker not ready.")
            return -1  # Indicate error or inability to check
        
        bar_hours = self.getPrice('1h', ts_start_utc, limit)
        
        if bar_hours is None:
            self.jdata.logError("hitChecker: Could not get hourly price data.")
            return -1  # Indicate error
        
        #for k_tp, e in enumerate(bar_hours): print(k_tp, e)  # k renamed to k_tp for clarity
        
        k_target_index = 0  # Index for the take_profit list
        for bar_h in bar_hours:
            if k_target_index >= len(take_profit):  # All take profit targets met or passed
                self.jdata.logInfo("All take profit targets processed.")
                return 1  # Or some other status indicating completion
            
            current_tp_target = take_profit[k_target_index]
            
            if stop_loss.price < bar_h.L and bar_h.H < current_tp_target.price:
                self.jdata.logInfo(f" Next Hour: target_idx = {k_target_index} bar time = {bar_h.D}\n"
                                   f" bar_h.L ({bar_h.L}) > stop_loss ({stop_loss.price}) and"
                                   f" bar_h.H ({bar_h.H}) < take_profit ({current_tp_target.price})")
                continue
            
            bar_minute_list = self.getPrice('1m', bar_h.Ts, 60)  # Renamed bar_minute to bar_minute_list
            if bar_minute_list is None or not bar_minute_list:
                self.jdata.logInfo(f"Could not get minute data for hour starting {bar_h.D} or no data returned.")
                continue  # Skip to next hour if minute data is unavailable
            
            self.jdata.logInfo(
                f" Read minutes: target_idx={k_target_index} bar_h= {bar_h.D} ({bar_h.Ts}) bar_m_start = {bar_minute_list[0].D} ({bar_minute_list[0].Ts})\n"
                f" bar_h.L ({bar_h.L}) <= stop_loss ({stop_loss.price}) or"
                f" take_profit ({current_tp_target.price}) <= bar_h.H ({bar_h.H})")
            
            for bar_m in bar_minute_list:
                if k_target_index < len(take_profit) and current_tp_target.price <= bar_m.H:  # Check index bound again
                    current_tp_target.time_hit = bar_m.Ts  # Use time_hit
                    self.jdata.logInfo(f"Take Profit: target_idx = {k_target_index} bar min time = {bar_m.D}\n"
                                       f" bar_m.H ({bar_m.H}) >= take_profit ({current_tp_target.price})")
                    k_target_index += 1
                    if k_target_index >= len(take_profit):  # Check if all TPs are hit
                        self.jdata.logInfo("All take profit targets hit.")
                        # Decide whether to return here or check stop_loss for this minute bar too
                
                if bar_m.L <= stop_loss.price:
                    stop_loss.time_hit = bar_m.Ts  # Use time_hit
                    self.jdata.logInfo(f"StopLoss Hit: bar min time = {bar_m.D}\n"
                                       f" bar_m.L ({bar_m.L}) <= stop_loss ({stop_loss.price})")
                    return 0  # Stop loss hit, exit
                
                if k_target_index >= len(take_profit):  # If all TPs hit, and SL not hit in this bar, can break inner loop
                    break
            
            self.jdata.logInfo(f" ==> Minute interval for hour {bar_h.D} is over. Next TP index = {k_target_index}\n")
            if k_target_index >= len(take_profit) and stop_loss.time_hit == 0:  # All TPs hit and no SL
                return 1  # Indicate success or completion
        
        self.jdata.logInfo('Finished processing all hourly bars.')
        return 1 if k_target_index > 0 and stop_loss.time_hit == 0 else -1

class Verify_Db(CfgJson,Dbase):
    # jclass: T.CfgJson # Class annotation, instance var below
    
    def __init__(self, cfg_file: str = None, cfg_mem = None, section='Verification' ):  # Use jdata_param to avoid conflict
        self.checker: TargetPriceChecker = None
        self._is_initialized: bool = False
        
        # It's better to initialize jdata here if cfg_file is provided

        CfgJson.__init__(self, cfg_file=cfg_file, cfg_mem=cfg_mem, section=section)
        Dbase.__init__(self, self, self.cfg_section)

        if self.db_ready:
            self.logInfo("Verify_Db: Database initialized successfully.")

            self.checker = TargetPriceChecker( self )
            if self.checker.isReady and self.db_Open():  # Open DB during init
                self._is_initialized = True
            else:
                self.logError("Verify_Db: Failed to initialize DB or Checker.")
        else:
            print("Verify_Db: jdata not provided or cfg_file couldn't be loaded.")

    """
        if cfg_file and not self.jdata:
            # Assuming 'path' should come from a config or be predefined
            # Placeholder for path:
            # project_base_path = "/your/project/path/" # This needs to be correctly defined
            # full_cfg_file_path = project_base_path + "Devl/Files/" + cfg_file # Example
            # self.jdata = T.CfgJson(full_cfg_file_path, section="ByBit") # Or relevant section
            pass  # Path logic needs to be resolved
        
        if self.jdata:
            self.db = Dbase(self.jdata, self.jdata.cfg_section)
            self.checker = TargetPriceChecker(self.jdata)
            if self.checker.isReady and self.db.db_Open():  # Open DB during init
                self._is_initialized = True
            else:
                self.jdata.logError("Verify_Db: Failed to initialize DB or Checker.")
        else:
            print("Verify_Db: jdata not provided or cfg_file couldn't be loaded.")
    """

    def process_records(self ):

        # remaping from db fields to internal vars
        pair='symbol'

        entryPrice = 'entryPrice'
        entryTime  = 'msgUtcTimeStamp'

        tpPrice = ['prPrice1', 'prPrice2', 'prPrice3']
        tpSize  = ['prSize1', 'prSize2', 'prSize3']
        stLossPrice = 'slPrice'

        if not self._is_initialized:
            self.logError("Verify_Db not initialized. Cannot process records.")
            return -1
        
        db_tables_def = self.cfg_section.get('Tables', None)
        if db_tables_def is None or len(db_tables_def) == 0:
            self.logError(f"Tables not found in configuration.")
            return -1
        
        db_table_i = list( db_tables_def[0].keys() )[0]
        self.set_Factory('dict')

        for record in self.QueryBy1(f"SELECT * FROM {db_table_i} where rId = 1 "):
            try:

                self.ProfMaxProc = 20
                self.ProfActProc = 30
                self.ProfTotalVol = 40
                
                self.LossActProc = 50
                self.LossTotalVol = 60

                pair_str = record[ pair ]
                start_time = int( record[entryTime] )     # utc timestamp in seconds
                entry_price = float( record[entryPrice] )
                                               
                profit_targets = [
                    pTarget(price=record[tpPrice[k]], size=record[tpSize[k]]) for k in range(len(tpPrice))
                ]
                stop_loss_target = pTarget( price=record[stLossPrice], size=100 )

                self.checker.setPair( record[ pair ] )
                self.checker.setStartTime( start_time )

                if self.checker.hitChecker(start_time, 24 + 60, profit_targets, stop_loss_target) == 0:
                    self.logInfo( f"hitChecker returned 0 (StopLoss hit or all TPs met) for record starting {start_time}")

                # calculate results for each take profit and stop loss
                for tp_item in profit_targets:
                    if tp_item.Hit:
                        tp_item.calculate( entry_price )  # Use fetched position_entry_price

                if stop_loss_target.Hit:
                    stop_loss_target.calculate( entry_price )  # Use fetched position_entry_price

                # calculate total values for open position:
                self.ProfMaxProc = max( pf.proc for pf in profit_targets ) #if pf.Hit
                self.ProfActProc = 30
                self.ProfTotalVol = sum( (pf.profit for pf in profit_targets if pf.Hit), 0)
                
                self.LossActProc = 50
                self.LossTotalVol = stop_loss_target.profit if stop_loss_target.Hit else 0

                # For logging, time_hit of position_entry_price is needed if it's a pTarget.
                # If it's just a price, then we don't have a timestamp for it here.
                self.logInfo(
                    f"Results for record: Pair: {pair_str}, StartTime: {T.UtcTimeStamp2Date(start_time)}\n"
                    f"Position Entry Price: { entry_price }\n"
                    f"{ table( [ [tp.time_hit] + \
                    [T.UtcTimeStamp2Date(tp.time_hit)] + [repr(tp)] for tp in profit_targets if tp.Hit])}\n"
                    f"Total profit = {self.ProfTotalVol:.4f}"
                    )
                
                # Update record with calculated values and update rec in db:
                self.UpdateRecord( db_table_i, record, profit_targets, stop_loss_target)

            except KeyError as e:
                self.logError(f"Missing column in record: {e}")
            except Exception as e:
                self.logError(f"Error processing record: {type(e).__name__} - {e}")
                traceback.print_exc()
            # end try
            #     
        # end for record in self.QueryBy1(f"SELECT * FROM {db_table_i}"):
        
        self.print_statistic( db_table_i )
        return 0
        # return -1 # Original return was here, but loop might complete successfully

    def UpdateRecord( self, table_name, record, p_targets, sl_target):

        stmt =  f"UPDATE {table_name} Set "
        stmt += f"ProfMaxProc = {self.ProfMaxProc:.2f}, "
        stmt += f"ProfActProc = {self.ProfActProc:.2f}, "
        stmt += f"ProfTotalVol= {self.ProfTotalVol:.4f}, "

        stmt += f"LossActProc = {self.LossActProc:.2f}, "
        stmt += f"LossTotalVol = {self.LossTotalVol:.4f}, "
        
        for k, p_target in enumerate( p_targets ):
            j = k+1
            stmt += f"prProc{j}    = {p_target.proc:.2f}, "
            stmt += f"prProf{j}    = {p_target.profit:.4f}, "
            stmt += f"prDate{j}    = '{T.UtcTimeStamp2Date(p_target.time_hit)}', "
            stmt += f"prTimeUtc{j} = {p_target.time_hit}, "

        stmt += f"slProc = {sl_target.proc:.2f}, "
        stmt += f"slLoss = {sl_target.profit:.4f}, "
        stmt += f"slDate = '{datetime.fromtimestamp(sl_target.time_hit)}', "
        stmt += f"slTimeUtc = {sl_target.time_hit} "

        stmt += f" where rId = {record['rId']}"

        cursor = self.Cursor()
        if 1 == self.ExecuteSql( stmt, commit=True, cursor=cursor).rowcount :
            self.Commit( cursor )

    def print_statistic(self, db_table ):

        tables_desc = self.cfg_section.get('Tables',None)
        if tables_desc is None:
            return

        for table_desc in tables_desc:
            if list( table_desc.keys() )[0] == db_table:
                fields_desc   = table_desc[ db_table ]
                headers = list( fields_desc.keys() )
                
                rec_all = self.QueryAll(f"SELECT * FROM {db_table}")
                
                formatted_data = [headers] + [ r for r in rec_all ]
        
                self.logInfo("\n" + table( formatted_data ) )
        
        
def table(values: list) -> str: # Added type hint
    if not values:
        return ""
    first = values[0]
    # Ensure consistent handling for list of lists or list of dicts
    if isinstance(first, dict):
        keys = list(first.keys())
        data_rows = [[str(v.get(k, '')) for k in keys] for v in values] # Handle missing keys
    elif isinstance(first, (list, tuple)):
        keys = range(len(first)) # Number of columns from first row
        data_rows = [[str(item) for item in row] for row in values]
    else:
        # Handle single list of items as a single row table, or raise error
        # For now, assume list of lists/dicts
        return "Table input format not supported or empty."

    # Calculate widths based on stringified data
    num_cols = len(data_rows[0])
    widths = [0] * num_cols
    for row in data_rows:
        for i, item_str in enumerate(row):
            if i < num_cols: # Ensure we don't go out of bounds if rows have varying lengths
                 widths[i] = max(widths[i], len(item_str))

    string_format = ' | '.join(['{:<' + str(w) + '}' for w in widths])
    return "\n".join([string_format.format(*row) for row in data_rows])

def print_date( t_date ):

    print(f"zone date {t_date}  in local zone: {T.Iso2LocalDate(t_date)}")
    print(f"zone date {t_date}  in utc   zone: {T.Iso2UtcDate(t_date)}")
    print(f"zone date {t_date}  utcTimestamp   {T.Iso2UtcTimeStamp(t_date)}")
    #print("bybit timestamp= ", ext_param['exchange']._exchange.parse8601( t_date) //1000 )


def start1( cfg: str):
    app = Verify_Db(cfg_file=cfg, section='ReadHistoryDb')

    if not app._is_initialized:
        print("Verify_Db initialization failed.")
        return
    
    app.process_records()

def start2( cfg: str):
    
    jdata = T.CfgJson(cfg, section="ByBit")
    app = Verify_Db( jdata_param=jdata )
    app.process_records()

    jdata.logInfo(" =======  Finish ====== ")


if __name__ == '__main__':
    
    cfg = "s:\\V3\\Files\\" + "ReadHistoryDb.json"
    start1( cfg )
    #start2( cfg )
    
    print (" =======  End ====== " )


@dataclass
class Verify_Db2:
    jclass: T.CfgJson
    
    def __init__(self, jclass=None, cfg_file=None):
        self.jclass = jclass
    
    def init(self, cfg=None):
        
        if cfg is None:
            return -1
        
        match cfg:
            case str() as cfg_file:
                self.jdata = T.CfgJson(cfg_file, section="ByBit")
            
            case T.CfgJson() as jdata:
                self.jdata = jdata
            
            case _:
                raise TypeError(f"Unsupported type for cfg: {type(cfg)}")
        
        # 2. Init DB with input table:
        db = Dbase(jdata, jdata.cfg_section)
        checker = TargetPriceChecker(jdata)
        
        if checker.isReady and db.db_Open():
            
            for record in db.QueryBy1(f"Select * from {table}"):
                
                #checker.setPair()
                #checker.setStartTime(record[aa])
                
                take_profit = [
                    pTarget(2.44, size=250),  # target  1
                    pTarget(2.45, size=500),  # target  2
                    pTarget(2.47, size=250)  # target  3
                ]
                
                stop_loss = pTarget(2.30)  # stop loss
                
                if checker.hitChecker(24 + 60, take_profit, stop_loss) == 0:
                    jdata.logInfo("return 0 ")
                
                total = 0
            
            return 0
        return -1


def table2(values):
    if not values:
        return ""
    
    first = values[0]
    keys = list(first.keys()) if isinstance(first, dict) else range(0, len(first))
    widths = [max([len(str(v[k])) for v in values]) for k in keys]
    string = ' | '.join(['{:<' + str(w) + '}' for w in widths])
    
    return "\n".join([string.format(*[str(v[k]) for k in keys]) for v in values])
