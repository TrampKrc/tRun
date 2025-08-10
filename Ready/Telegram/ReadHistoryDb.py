import asyncio

from sqliteSupport import Table
from THistoryDb import THistoryDb

import tools as T, TMessage as M


#
# collect data to db and print
#
# Channel 'Мастерство трейдинга': -1001500911313

#   any parser creates class to keep data for an order:
#    data = M.Order_Info()
#   process_msg unions channel data ( tdata = M.TMsg_Info(msg) )
#   with an order data to dict
#   MakeRecord maps data to db record structure
#   which is defined in config json.
#   that db will be used as input for verification.
#   db path = { CfgFolder } + {DbFile}:


class ReadHistoryDb( THistoryDb ):
    
    # ============================ should be defined
    def dbTableInit(self, sectionTables):
        # Create internal structures of table base on description from cfg file
        self.table1 = Table(sectionTables[0])

    def dbTableCreate(self):
        self.table1.Create(self.db.cursor)
    
    # is calling from dbOpen after db_Open()
    def dbTableOpen(self):
        self.table1.Drop(self.db.cursor)
        self.table1.Create(self.db.cursor)


    def dbTableAdd(self, record):
        self.table1.Insert(self.db.cursor, record )

    
    # is calling from dbClose before db_Close()
    def dbTableClose(self):
        # Post-processing
        # all msgs are done !
        
        if len(self.history_msgs) > 0:
            
            self.history_msgs.reverse()
            
            n = len(self.history_msgs)
            print(T.yellow(f"Results: {n}"))
            self.logInfo(f"Results: {n}")
            
            with open(self.channel_cfg["CfgFolder"] + self.channel_cfg["HistoryFile"], 'wt', encoding="utf-8") as fout:
                dbRecords = []
                for data in self.history_msgs:
                    s = f" {data['tdata']._channel_msgId} {data['tdata']._channel_date} => {data['tdata']} \n"
                    print(T.green(s))
                    self.logInfo(s)
                    
                    fout.write(f'==> {data['tdata']._channel_date} {data['tdata']._channel_utctime}\n'
                               f'teleg  msg:\n {data['tdata']}\n'
                               f'order data:\n {data['odata']}\n'
                               f'====================\n')
                    
                    record = self.MakeRecord( data )
                    dbRecords.append( record )

            self.dbTableAdd( dbRecords)
            
    def MakeRecord(self, data ):

        tdata = data['tdata']
        odata = data['odata']

        # mapping from TMsg_Info class and Order_Info class
        rec = self.table1.getNewRecord()

        rec.ChannelId = self.channel_cfg["Id"]
        rec.ChannelName = self.channel_cfg["Name"]

        rec.msgId = tdata._channel_msgId
        rec.msgDate = tdata._channel_date
        rec.msgUtcTimeStamp = tdata._channel_utc_timestamp

        rec.symbol    = odata.symbol
        rec.orderSide = odata.order_side
        rec.orderType = odata.order_type.value
        rec.direction = odata.direction.value
        rec.volume    = odata.entry_volume
        rec.leverage  = odata.entry_leverage

        rec.entryPriceMin = min( odata.entry_price[0], odata.entry_price[1] )
        rec.entryPriceMax = max( odata.entry_price[0], odata.entry_price[1] )

        if rec.entryPriceMin > 0:
            rec.entryPrice = ( rec.entryPriceMin + rec.entryPriceMax) /2
        else: rec.entryPrice = rec.entryPriceMax

        for k in range(3):
            if k < len(odata.tpPrice):
                rec["prPrice"+str(k+1)] = odata.tpPrice[k][0]
                rec["prSize"+str(k+1)] = odata.tpPrice[k][1]

                rec["prProc"+str(k+1)] = 0.
                rec["prProf"+str(k+1)] = 0.
                rec["prDate"+str(k+1)] = ''
                rec["prTimeUtc"+str(k+1)] = 0

        rec.slPrice = odata.slPrice[0]
        rec.slSize = odata.slPrice[1] if len(odata.slPrice) > 1 else 0
        rec.slProc = 0.
        rec.slLoss = 0.
        rec.slDate = ''
        rec.slTimeUtc = 0

        rec.ProfMaxProc = 0.
        rec.ProfActProc = 0.
        rec.ProfTotalVol = 0.

        rec.LossActProc = 0.
        rec.LossTotalVol = 0.

        rec.body = tdata.Body
        rec.note = " "   

        return rec
        
    # msg processing; called from THistory->Run
    def process_msg(self, msg):
        # the msg is not empty and msg.date has been checked
        
        # if self.section_cfg["UserId"] in [0, msg.from_user.id ]:
        if self.section_cfg["UserId"] == 0 or self.section_cfg["UserId"] == msg.from_user.id:
            
            # the msg.date has been checked
            tdata = M.TMsg_Info(msg)
            
            odata = self.channel_parser(self, msg)
            
            if odata:
                self.history_msgs.append({'tdata': tdata, 'odata': odata})
                
                return True
        
        return False
    
    # ============================ should be defined
    
    def __init__(self, cfg_file=None, section=None, jclass=None, parser=None ) -> None:

        super().__init__( cfg_file=cfg_file, section=section, jclass=jclass )

        self.channel_parser = parser
        self.history_msgs = []


async def historyDb_main( cl_parser ):
    
    
    #cfg_file = os.getcwd()+"/Files/ReadHistoryDb.json"
    cfg_file = T.CfgFolder + "ReadHistoryDb.json"
    Bot = ReadHistoryDb( cfg_file, "ReadHistoryDb", parser = cl_parser )
    await Bot.Start()


async def historyDb_test( cl_parser ):
    cfg_test = {
        "Secrets":       "s:\\V3\\Files\\secrets.json",
        
        "ReadHistoryDb": {
            "UserId":         0,
            "Name":           "Мастерство трейдинга",
            "Id":             -1001500911313,
            "CfgFolder":       "S:\\V3\\Files\\ReadHistoryDb\\",
            "OutFolder":        "l-H1-",
            "HistoryFile":    "h-H1.txt",
            
            "HistoryLimit":   2000000,
            "HistoryStart":   "2024-05-01 00:00:00-07:00",
            "HistoryEnd":     "2024-05-11 00:01:00-07:00",
            
            "DbFile":         "ReadHistoryDbT1.db",
            "Tables":         [{
                "H1_I": {
                    "rId":       "int Primary Key",
                    "msgId":     "int",
                    
                    "tDate":     "text",
                    "utcDate":   "text",
                    
                    "symbol":    "text",
                    "orderSide": "int",
                    "orderType": "int",
                    "direction": "integer",
                    
                    "openMin":   "real",
                    "openMax":   "real",
                    "take1":     "real",
                    "vol11":     "real",
                    "take2":     "real",
                    "vol12":     "real",
                    "take3":     "real",
                    "vol13":     "real",
                    "stloss":    "real",
                    
                    "open":      "real",
                    "dateTake1": "text",
                    "dateTake2": "text",
                    "dateTake3": "text",
                    
                    "priceMin":  "real",
                    "dateMin":   "text",
                    
                    "body":      "text",
                    "note":      "text"
                }
            },
                
                {
                    "H1_O": {
                        "RecId":          "integer PRIMARY KEY",
                        "I_RecId":        "integer",
                        "Open":           "real",
                        "Close":          "real",
                        "Delta":          "real",
                        "DeltaProc":      "real",
                        "Open_Min":       "real",
                        "Open_Max":       "real",
                        "Close_Min":      "real",
                        "Close_Max":      "real",
                        "Frame_Min":      "real",
                        "Frame_Min_Date": "text",
                        "Frame_Max":      "real",
                        "Frame_Max_Date": "text"
                    }
                }
            ],
            
            "MonitorMinutes": 0
        }
    }

    T.print_green('HistoryDB TestA')
    
    jclass = T.CfgJson(cfg=cfg_test, section="ReadHistoryDb")
    
    Bot = ReadHistoryDb(jclass=jclass, parser=cl_parser)
    await Bot.Start()


if __name__ == '__main__':

    # Channel 'Мастерство трейдинга': -1001500911313
    #from p_crypto_daniel import crypto_daniel cl_parser

    # Channel 'Мастерство трейдинга': -1001500911313
    #from p_master_trade import master_trading as cl_parser

    asyncio.run( historyDb_main( cl_parser ) )

    #asyncio.run( historyDb_test( cl_parser ) )
    # test_parser()
