import sqlite3
import os

# Connect to the database
db_path = "../league_cache.db"
print(f"Checking database at: {os.path.abspath(db_path)}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables:")
    for table in tables:
        table_name = table[0]
        print(f"  - {table_name}")
        
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print(f"    Columns: {len(columns)}")
        for col in columns:
            print(f"      {col[1]} ({col[2]})")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"    Rows: {count}")
        print()
    
    conn.close()
    print("✅ Database check complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
