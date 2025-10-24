"""
SQLite Database Explorer for Clinical Decision Support System
Run this script to explore the database content interactively
"""

import sqlite3
import pandas as pd
from datetime import datetime
import json

def connect_to_database():
    """Connect to the SQLite database"""
    try:
        conn = sqlite3.connect('pdpcds_dev.db')
        conn.row_factory = sqlite3.Row  # This allows column access by name
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def show_tables(conn):
    """Display all tables in the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("📋 Available Tables:")
    print("=" * 50)
    for table in tables:
        print(f"  • {table[0]}")
    return [table[0] for table in tables]

def show_table_schema(conn, table_name):
    """Display the schema of a specific table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    
    print(f"\n🏗️  Schema for table '{table_name}':")
    print("=" * 60)
    print(f"{'Column':<20} {'Type':<15} {'Null':<8} {'Default':<15} {'PK':<4}")
    print("-" * 60)
    
    for col in columns:
        not_null = "NOT NULL" if col[3] else "NULL"
        default = col[4] if col[4] else ""
        pk = "PK" if col[5] else ""
        print(f"{col[1]:<20} {col[2]:<15} {not_null:<8} {str(default):<15} {pk:<4}")

def show_table_data(conn, table_name, limit=10):
    """Display sample data from a table"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    total_rows = cursor.fetchone()[0]
    
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    rows = cursor.fetchall()
    
    print(f"\n📊 Data from table '{table_name}' (showing {len(rows)} of {total_rows} rows):")
    print("=" * 80)
    
    if rows:
        # Convert to pandas DataFrame for better display
        df = pd.DataFrame([dict(row) for row in rows])
        
        # Handle JSON columns for better display
        for col in df.columns:
            if any(isinstance(val, str) and val.startswith(('[', '{')) for val in df[col] if pd.notna(val)):
                df[col] = df[col].apply(lambda x: json.loads(x) if pd.notna(x) and isinstance(x, str) else x)
        
        print(df.to_string(max_rows=limit, max_cols=10, width=100))
    else:
        print("  No data found in this table.")

def interactive_query(conn):
    """Allow user to run custom SQL queries"""
    print(f"\n💻 Interactive SQL Query Mode")
    print("=" * 50)
    print("Enter your SQL queries (type 'exit' to quit):")
    print("Example: SELECT * FROM predictions LIMIT 5;")
    
    while True:
        query = input("\n🔍 SQL> ").strip()
        
        if query.lower() == 'exit':
            break
            
        if not query:
            continue
            
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.upper().startswith('SELECT'):
                rows = cursor.fetchall()
                if rows:
                    df = pd.DataFrame([dict(row) for row in rows])
                    print(f"\n📊 Query Results ({len(rows)} rows):")
                    print("-" * 50)
                    print(df.to_string(max_rows=50, width=120))
                else:
                    print("No results found.")
            else:
                conn.commit()
                print(f"✅ Query executed successfully. Rows affected: {cursor.rowcount}")
                
        except sqlite3.Error as e:
            print(f"❌ SQL Error: {e}")

def main():
    """Main function to explore the database"""
    print("🏥 Clinical Decision Support System - Database Explorer")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️  Database: pdpcds_dev.db")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Show available tables
        tables = show_tables(conn)
        
        if not tables:
            print("No tables found in the database.")
            return
        
        # Show schema and data for each table
        for table in tables:
            show_table_schema(conn, table)
            show_table_data(conn, table, limit=5)
            print("\n" + "=" * 80)
        
        # Interactive query mode
        interactive_query(conn)
        
    finally:
        conn.close()
        print("\n✅ Database connection closed.")

if __name__ == "__main__":
    main()