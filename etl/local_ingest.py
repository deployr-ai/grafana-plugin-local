import pandas as pd
import psycopg2
from datetime import datetime
import sys
import os

DB_CONFIG = {
    "dbname": "timescale_db",
    "user": "admin",
    "password": "admin",
    "host": "localhost",
    "port": 5432
}

def load_csv_to_timescale(csv_file_path="asda.csv"):
    """
    Load data from CSV file into TimescaleDB with the same structure as download.py
    """
    try:
        # Check if CSV file exists
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file '{csv_file_path}' not found.")
            return False
            
        print(f"Loading data from {csv_file_path}...")
        
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Loaded {len(df)} rows from CSV")
        
        # Get unique assets
        unique_assets = df['Asset'].unique()
        print(f"Found {len(unique_assets)} unique assets: {list(unique_assets)}")
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connected to TimescaleDB")
        
        # Process each asset
        for asset in unique_assets:
            asset_db = asset.upper().replace(".", "_")  # For database table name
            asset_data = df[df['Asset'] == asset].copy()
            
            print(f"Processing {asset} ({len(asset_data)} rows)...")
            
            # Create table for this asset
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS sp500_{asset_db} (
                    time TIMESTAMPTZ PRIMARY KEY,
                    open DOUBLE PRECISION NULL,
                    high DOUBLE PRECISION NULL,
                    low_price DOUBLE PRECISION NULL,
                    close_price DOUBLE PRECISION NULL,
                    volume DOUBLE PRECISION NULL
                );
            """)
            
            # Clear existing data for this asset (optional - remove if you want to append)
            cursor.execute(f"DELETE FROM sp500_{asset_db}")
            
            # Insert data
            inserted_count = 0
            skipped_count = 0
            
            for index, row in asset_data.iterrows():
                try:
                    # Convert date string to proper format
                    date_str = row['Date']
                    if isinstance(date_str, str):
                        # Handle timezone info in the date string
                        if '-04:00' in date_str or '-05:00' in date_str:
                            # Remove timezone info for simpler handling
                            date_str = date_str.split(' ')[0] + ' ' + date_str.split(' ')[1]
                            date_str = date_str.replace('-04:00', '').replace('-05:00', '')
                        
                        # Parse the datetime
                        timestamp = pd.to_datetime(date_str).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        timestamp = pd.to_datetime(row['Date']).strftime('%Y-%m-%d %H:%M:%S')
                    
                    cursor.execute(f"""
                        INSERT INTO sp500_{asset_db} (time, open, high, low_price, close_price, volume)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (time) DO UPDATE SET
                            open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low_price = EXCLUDED.low_price,
                            close_price = EXCLUDED.close_price,
                            volume = EXCLUDED.volume
                    """, (
                        timestamp,
                        float(row['Open']),
                        float(row['High']),
                        float(row['Low']),
                        float(row['Close']),
                        float(row['Volume'])
                    ))
                    inserted_count += 1
                    
                except Exception as e:
                    print(f"Error inserting row for {asset}: {e}")
                    skipped_count += 1
                    continue
            
            print(f"[{asset}] ✓ Inserted {inserted_count} rows, skipped {skipped_count}")
            
        # Commit all changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ Data successfully loaded into TimescaleDB!")
        print("Tables created with pattern: sp500_{ASSET_SYMBOL}")
        
        return True
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def verify_data():
    """
    Verify that data was loaded correctly by showing table counts
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get all sp500 tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name LIKE 'sp500_%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\nFound {len(tables)} SP500 tables:")
        
        total_rows = 0
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            asset_name = table_name.replace('sp500_', '')
            print(f"  {asset_name}: {count} rows")
            total_rows += count
            
        print(f"\nTotal rows across all tables: {total_rows}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error verifying data: {e}")

if __name__ == "__main__":
    # Allow custom CSV file path as command line argument
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/local_data.csv"
    
    print("=== TimescaleDB Local CSV Ingestion ===")
    print(f"CSV file: {csv_path}")
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")
    print()
    
    # Load the data
    success = load_csv_to_timescale(csv_path)
    
    if success:
        print("\n=== Verification ===")
        verify_data()
    else:
        print("❌ Data loading failed!")
        sys.exit(1) 