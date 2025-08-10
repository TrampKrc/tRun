import sqlite3
import time


def demonstrate_fetch_behavior(db_path, table_name):
    """
    Demonstrate that execute() doesn't fetch data, only prepares the query
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Step 1: Executing query (no data fetched yet)")
        start_time = time.time()
        cursor.execute(f"SELECT * FROM {table_name}")
        execute_time = time.time() - start_time
        print(f"Execute time: {execute_time:.6f} seconds")
        print("Query executed, but no data in memory yet!\n")
        
        print("Step 2: Fetching records one by one")
        record_count = 0
        while True:
            start_fetch = time.time()
            record = cursor.fetchone()  # This is when data is actually retrieved
            fetch_time = time.time() - start_fetch
            
            if record is None:
                break
            
            record_count += 1
            print(f"Fetched record #{record_count}: {record} (fetch time: {fetch_time:.6f}s)")
        
        print(f"\nTotal records processed: {record_count}")
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def compare_fetch_methods(db_path, table_name):
    """
    Compare different fetch methods to show the difference
    """
    try:
        conn = sqlite3.connect(db_path)
        
        # Method 1: fetchone() - truly one by one
        print("Method 1: fetchone() - One record at a time")
        cursor1 = conn.cursor()
        cursor1.execute(f"SELECT * FROM {table_name}")
        
        count = 0
        while True:
            record = cursor1.fetchone()  # Fetches only ONE record from database
            if record is None:
                break
            count += 1
            print(f"  Retrieved record #{count}")
        
        # Method 2: fetchall() - all at once
        print(f"\nMethod 2: fetchall() - All records at once")
        cursor2 = conn.cursor()
        cursor2.execute(f"SELECT * FROM {table_name}")
        
        all_records = cursor2.fetchall()  # Fetches ALL records from database at once
        print(f"  Retrieved {len(all_records)} records in one operation")
        
        # Method 3: fetchmany() - batch by batch
        print(f"\nMethod 3: fetchmany(2) - Batch processing")
        cursor3 = conn.cursor()
        cursor3.execute(f"SELECT * FROM {table_name}")
        
        batch_num = 1
        while True:
            batch = cursor3.fetchmany(2)  # Fetches 2 records at a time
            if not batch:
                break
            print(f"  Batch #{batch_num}: {len(batch)} records")
            batch_num += 1
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def read_records_one_by_one(db_path, table_name):
    """
    Read records one by one from SQLite database
    """
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute query to select all records
        cursor.execute(f"SELECT * FROM {table_name}")
        
        # Method 1: Using fetchone() in a loop
        print("Method 1: Using fetchone()")
        print("-" * 30)
        
        while True:
            record = cursor.fetchone()
            if record is None:
                break
            print(f"Record: {record}")
        
        # Reset cursor for second method
        cursor.execute(f"SELECT * FROM {table_name}")
        
        print("\nMethod 2: Using cursor as iterator")
        print("-" * 30)
        
        # Method 2: Using cursor as iterator
        for record in cursor:
            print(f"Record: {record}")
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def create_sample_database():
    """
    Create a sample database with test data
    """
    conn = sqlite3.connect('sample.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER
        )
    ''')
    
    # Insert sample data
    sample_data = [
        (1, 'John Doe', 'john@example.com', 30),
        (2, 'Jane Smith', 'jane@example.com', 25),
        (3, 'Bob Johnson', 'bob@example.com', 35),
        (4, 'Alice Brown', 'alice@example.com', 28)
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)', sample_data)
    conn.commit()
    conn.close()
    print("Sample database created successfully!")


def read_with_processing(db_path, table_name):
    """
    Read records one by one with custom processing
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name}")
        
        record_count = 0
        while True:
            record = cursor.fetchone()
            if record is None:
                break
            
            record_count += 1
            
            # Process each record (example: print formatted output)
            if len(record) >= 4:  # Assuming users table structure
                id, name, email, age = record[:4]
                print(f"User #{record_count}: {name} ({age} years old) - {email}")
            else:
                print(f"Record #{record_count}: {record}")
            
            # You can add any processing logic here
            # For example: validation, transformation, etc.
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


# Example usage
if __name__ == "__main__":
    # Create sample database
    create_sample_database()
    
    print("DEMONSTRATION: How execute() and fetch() work")
    print("=" * 50)
    demonstrate_fetch_behavior('sample.db', 'users')
    
    print("\n" + "=" * 50)
    print("COMPARISON: Different fetch methods")
    print("=" * 50)
    compare_fetch_methods('sample.db', 'users')
    
    print("\n" + "=" * 50)
    print("ORIGINAL: Reading records one by one")
    print("=" * 50)
    read_records_one_by_one('sample.db', 'users')
    
    print("\n" + "=" * 50)
    print("CUSTOM PROCESSING: Reading with formatting")
    print("=" * 50)
    read_with_processing('sample.db', 'users')
    
    
##================================================
# Using Context Manager for Better Resource Management
from contextlib import contextmanager
import sqlite3

@contextmanager
def db_connection(db_path):
    """Context manager for database connections"""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def process_users_batch():
    """Generator that processes users in batches"""
    with db_connection('mydb.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY id')
        
        while True:
            record = cursor.fetchone()
            if record is None:
                break
            yield record

# Processing records one by one
for user in process_users_batch():
    # Process each user record
    user_id, name, email = user
    print(f"Processing user {name}")
    # Your processing logic here

#============================================
# Batch Processing with Yield
def fetch_records_in_batches(db_path, batch_size=1000):
    """Fetch records in batches but yield them one by one"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        offset = 0
        while True:
            cursor.execute(f'''
                    SELECT * FROM large_table
                    LIMIT {batch_size} OFFSET {offset}
                ''')
            
            batch = cursor.fetchall()
            if not batch:
                break
            
            for record in batch:
                yield record
            
            offset += batch_size
    
    finally:
        conn.close()
    
    # Process large table efficiently
    for record in fetch_records_in_batches('mydb.sqlite', batch_size=500):
        # Process each record
        process_single_record(record)
        
##=============================================
# With Row Factory(Dictionary - like Access)

def fetch_records_as_dict(db_path, query):
    """Yields records as dictionaries for easier field access"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Makes rows dict-like
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        while True:
            record = cursor.fetchone()
            if record is None:
                break
            yield dict(record)
    finally:
        conn.close()


# Usage
for user in fetch_records_as_dict('mydb.sqlite', 'SELECT id, name, email FROM users'):
    print(f"User {user['name']} has email {user['email']}")
    
    
##===========================================================
###       Common Use Cases

# Infinite Sequences:
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Get first 10 Fibonacci numbers
fib = fibonacci()
for i in range(10):
    print(next(fib))
    
#  Processing Large Files:
def read_large_file(filename):
    with open(filename, 'r') as file:
        for line in file:
            yield line.strip()

# Memory-efficient file processing
for line in read_large_file('huge_file.txt'):
    process(line)
    
# Data Transformation:
def square_numbers(numbers):
    for num in numbers:
        yield num ** 2

# Transform data on-demand
squares = square_numbers([1, 2, 3, 4, 5])
print(list(squares))  # [1, 4, 9, 16, 25]


#  Advanced Features
# Yield Expressions (receiving values):
def coroutine():
    while True:
        value = yield
        print(f"Received: {value}")

# Send values to generator
gen = coroutine()
next(gen)  # Prime the generator
gen.send("Hello")  # Prints: Received: Hello

# Yield From (delegating to another generator):
def inner_gen():
    yield 1
    yield 2

def outer_gen():
    yield from inner_gen()
    yield 3

# Equivalent to yielding 1, 2, 3