import yfinance as yf
import time
import psycopg2

DB_CONFIG = {
    "dbname": "timescale_db",
    "user": "admin",
    "password": "admin",
    "host": "localhost",
    "port": 5432
}

asset="TSLA"

def get_sp500_data():
    asset_tracker = yf.Ticker(asset)
    data = asset_tracker.history(period="6mo")
    return data


def save_to_timescaledb(data):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sp500_prices (
                time TIMESTAMPTZ PRIMARY KEY,
                close_price DOUBLE PRECISION NULL,
                asset TEXT NULL                
            );
        """)
        conn.commit()

        for index, row in data.iterrows():
            cursor.execute(f"""INSERT INTO sp500_prices (time, close_price, asset)
                VALUES ('{index}', '{float(row["Close"])}', '{asset}')
                ON CONFLICT (time) DO UPDATE SET close_price = EXCLUDED.close_price;
            """,)
            print(index,float(row["Close"]), asset)

        conn.commit()
        cursor.close()
        conn.close()
        print("Datos guardados en TimescaleDB.")

    except Exception as e:
        print("Error al insertar en TimescaleDB:", e)

if __name__ == "__main__":
    while True:
        sp500_data = get_sp500_data()
        save_to_timescaledb(sp500_data)
        time.sleep(86400) 
