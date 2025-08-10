import copy
import sqlite3
from sqlite3 import Error
from collections import namedtuple
import datetime

import tools as T
"""
tb_cfg = {
    "TableName": {
        'F1" : 'int',
        'F2' :'real'
    }    
}
"""
class Table():

    def __init__(self, cfg: dict = None, db = None ):
        if cfg is not None:
            self.Init( cfg, db )

    def Init(self, cfg: dict, dbase = None):
        def f_type( key ):
            ftype = self.fields[key].split()[0].upper()

            if 'INT' in ftype:
                return 0
            if 'REAL' in ftype:
                return 0.0
            if 'TEXT' in ftype:
                return ""
            return 0

        self.table_name = list( cfg.keys() )[0]
        self.fields = cfg[ self.table_name ]
        self.fname_list = list( self.fields.keys() )
        self.primary = 0

        fields_list = ', '.join( self.fname_list )
        fields_mark = ', '.join( list( map( lambda e: '?', self.fname_list)))
        self.insert = f"INSERT INTO {self.table_name}( {fields_list} ) VALUES( {fields_mark} )"
        # 'INSERT INTO employees(id, name, salary, department, position, hireDate) VALUES(?, ?, ?, ?, ?, ?)', data )

        #fields_list = ', '.join( list( map( lambda e: e[0], self.fields.items() ) ))
        #fields_mark = ', '.join( list( map( lambda e: '?', self.fields.items() ) ))

        self.record = dict( map( lambda n: ( n, f_type(n) ), self.fname_list[1:] ) )    # skip RecId - primary key
        #t_d = dict( map( lambda n: ( n, 0 ), self.fields.items() ) )
        #self.record = tools.mash(t_d)

        self.Attach( dbase )

    def Attach(self, dbase ):
        self.dbase = dbase

    def getNewRecord(self):
        return T.mash( copy.deepcopy(self.record) )

    def Drop(self, cursor=None ):
        cursor = cursor if cursor is not None else self.dbase.cursor

        cursor.execute( f'drop table if exists {self.table_name}')
        cursor.connection.commit()

    def Create(self, cursor=None ):
        cursor = cursor if cursor is not None else self.dbase.cursor

        stmt = self.table_name + "( " + ", ".join( list( map( lambda e: f'{e[0]} {e[1]}', self.fields.items()))  )
        cursor.execute("CREATE TABLE if not exists " + stmt + " )")
        #cursor.execute("CREATE TABLE if not exists " + employees(id integer PRIMARY KEY, name text, salary real, department text, position text, hireDate text)")
        cursor.connection.commit()

    def Insert(self, cursor=None, /, data=None, stmt=None ):
        cursor = cursor if cursor is not None else self.dbase.cursor

        if( data is not None ):
            sql = stmt if stmt is not None else self.insert

            if( type( data ) == list ):
                data_all = []
                for e in data:
                    l_data = list(map(lambda field: e[field], self.fname_list[1:]))
                    self.primary += 1
                    data_all.append( [self.primary] + l_data )

                cursor.executemany( sql, data_all )
            else:
                l_data = list( map( lambda field: data[field], self.fname_list ))
                #l_data = list( map( lambda field: data[field], self.fname_list[1:] ))
                #self.primary += 1
                #l_data = [self.primary] + l_data

                cursor.execute( sql, l_data )

        else:
            self.ExecuteSql( cursor, stmt )
        cursor.connection.commit()

    def Select(self, cursor=None):
        cursor = cursor if cursor is not None else self.dbase.cursor

        rc = cursor.connection.execute( f"SELECT * from {self.table_name}" )
        return rc.fetchall()

    def ExecuteSql(self, stmt, commit=False, cursor=None ):
        cursor = cursor if cursor is not None else self.dbase.cursor

        rc = cursor.executescript( stmt )
        if( rc > -1 and commit ): rc = cursor.connection.commit()
        return rc

"""
db_cfg = { 
   'CfgFolder': ' dir',
   'DbFile'  : 'file'
"""
class Dbase():
    #           papa - class based on CfgJson, cfg:{ "CfgFolder", "DbFile" }
    def __init__(self, papa, cfg ) -> None:
        # super().__init__()

        self.connection = None
        self.cursor     = None

        self.papa = papa

        self.db_file = cfg.get("DbFile", None)

        #self.db_ready = False if self.db_file is None else True
        if( self.db_file is not None ) :
            self.db_file = cfg.get("CfgFolder", ".\\") + self.db_file
            self.db_ready = True
        else:
            self.db_ready = False
            papa.logError(" Key DbFile is not defined at Dbase.__init__")

    def db_Open(self):

        def namedtuple_factory(cursor, row):
            fields = [column[0] for column in cursor.description]
            cls = namedtuple("Row", fields)
            return cls._make(row)

        try:
            # con = sqlite3.connect( ":memory:" )  # db in memory
            # create db if file doesnt exist
            self.connection = sqlite3.connect( self.db_file )
            self.connection.row_factory = self.namedtuple_factory
            # self.conn.row_factory = sqlite3.Row  # Makes rows dict-like
            self.cursor = self.connection.cursor()

        except Error:
            print(Error)
            self.db_ready = False

        return self.db_ready

    def namedtuple_factory( self, cursor, row):
        fields = [column[0] for column in cursor.description]
        cls = namedtuple("Row", fields)
        return cls._make(row)
    
    def set_Factory(self, factory:str):
        match factory:
            case 'class':
                self.connection.row_factory = self.namedtuple_factory
            case 'dict':
                self.connection.row_factory = sqlite3.Row  # Makes rows dict-like
            case _:
                self.connection.row_factory = self.namedtuple_factory
            
            
    def db_Close(self):

        self.connection.commit()
        self.connection.close()

    def QueryBy1(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            while True:
                record = cursor.fetchone()
                if record :
                    #yield dict(record)
                    yield record
                else:
                    break
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        
        return None
    
    def QueryByN(self, query, num:int=1):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            while records := cursor.fetchmany( num ) is not None:
                # yield dict(record)
                yield records
        
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        
        return None
    
    def QueryAll(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            all_records = cursor.fetchall()
            return all_records

        except sqlite3.Error as e:
            print(f"Database error: {e}")

        return None

    def QueryBatch(self, query, batch_size=1000):
        """Fetch records in batches but yield them one by one"""
        try:
            offset = 0
            cursor = self.connection.cursor()
            while True:
                cursor.execute(f"{query} LIMIT {batch_size} OFFSET {offset}")
                batch = cursor.fetchall()
                
                if not batch:
                    break
                
                for record in batch:
                    yield record
                
                offset += batch_size

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            
        return None

    def Cursor(self):
        if self.connection is not None:
            return self.connection.cursor()
        else:
            raise Error("Database connection is not established.")


    def ExecuteSql(self, stmt, commit=False, cursor=None ):
        cursor = cursor if cursor is not None else self.connection.cursor()
        return cursor.execute( stmt )
    
    def Commit(self, cursor=None ):
        if cursor is not None: rc = cursor.connection.commit()
        else : rc = self.connection.commit()
        return rc
    
    def RollBack(self, cursor=None ):
        if cursor is not None: rc = cursor.connection.rollback()
        else : rc = self.connection.rollback()
        return rc
    
#==============================================
def open_db( file_n ):

    try:
        # con = sqlite3.connect( ":memory:" )  # db in memory
        # create db if file doesnt exist
        con = sqlite3.connect( file_n )
        return con
    except Error:
        print(Error)
        return None

def table_create( con, sql_script ):
    cursorObj = con.cursor()
    cursorObj.execute( "Create Table if not exists " + sql_script )
    #cursorObj.execute("CREATE TABLE employees(id integer PRIMARY KEY, name text, salary real, department text, position text, hireDate text)")
    #cursorObj.execute('Create Table if not exists projects(id integer, name text)')
    con.commit()

def table_insert(con, entities):
    cursorObj = con.cursor()
    cursorObj.execute('INSERT INTO employees(id, name, salary, department, position, hireDate) VALUES(?, ?, ?, ?, ?, ?)', entities)
    con.commit()
    #entities = (2, 'Andrew', 800, 'IT', 'Tech', '2018-02-06')
    #table_insert(con, entities)


def table_update(con):
    cursorObj = con.cursor()
    cursorObj.execute('UPDATE employees SET name = "Rogers" where id = 2')
    con.commit()

def table_delete(con):
    cursorObj = con.cursor()
    cursorObj.execute('UPDATE employees SET name = "Rogers" where id = 2')
    con.commit()


def tt( cursorObj ):
    cursorObj.execute('SELECT name from sqlite_master where type= "table"')
    cursorObj.execute('SELECT name from sqlite_master WHERE type = "table" AND name = "employees"')
    print(cursorObj.fetchall())


    data = [(1, "Ridesharing"), (2, "Water Purifying"), (3, "Forensics"), (4, "Botany")]
    cursorObj.executemany("INSERT INTO projects VALUES(?, ?)", data)
    #con.commit()

    res = cursorObj.execute("SELECT * from t1")
    print( res.fetchall() )

    data1 = [ (100, 200, 300),
         (500, 600, 700)
       ]

#cur.executemany("INSERT INTO t1 VALUES(?, ?, ?)", data)
##cur.executemany("INSERT INTO IBC VALUES(:name, :year)", data)
#con.commit()

#for row in cur.execute("SELECT * FROM t1 ORDER BY field1"):
#    print(row)
    
    data = [ ('from', 'btc', 'data', 'buy', 'long', 123.22, 10.0, 50.0, None, None, 0.0, 'comment' ) ]
#cur.executemany("INSERT INTO IBC VALUES( ?,?,?,?,?,?,?,?,?,?,?,?)", data )
#con.commit()

    #for row in cur.execute("SELECT * FROM IBC"):
    #    print(row)

    """#cur.execute(""
    #    INSERT INTO movie VALUES
    #    ('Monty Python and the Holy Grail', 1975, 8.2),
    #    ('And Now for Something Completely Different', 1971, 7.5)
    #"")

    data = [
        ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
        ("Monty Python's The Meaning of Life", 1983, 7.5),
        ("Monty Python's Life of Brian", 1979, 8.0),
    ]
    cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)
    con.commit()  # Remember to commit the transaction after executing INSERT.


from collections import namedtuple

def namedtuple_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    cls = namedtuple("Row", fields)
    return cls._make(row)
namedtuple_factory() can be used as follows:

>>>
con = sqlite3.connect(":memory:")
con.row_factory = namedtuple_factory
cur = con.execute("SELECT 1 AS a, 2 AS b")
row = cur.fetchone()

     --cur.fetchmany(size=cursor.arraysize)¶
     --cur.fetchall()

row
Row(a=1, b=2)
row[0]  # Indexed access.
1
row.b   # Attribute access.
2
con.close()


for row in cur.execute("SELECT t FROM data"):
    print(row)


import sqlite3 as sqlite

conn = sqlite.connect('companies_db.sqlite')

with conn:
    conn.row_factory = sqlite.Row
    curs = conn.cursor()
    curs.execute("SELECT * FROM companies_table")
    rows = curs.fetchall()
    for row in rows:
        print(f"{row['companyid']}, {row['name']}, {row['address']}.")




    """


