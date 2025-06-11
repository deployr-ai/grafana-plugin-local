import yfinance as yf
import pandas as pd
import time
import psycopg2

DB_CONFIG = {
    "dbname": "timescale_db",
    "user": "admin",
    "password": "admin",
    "host": "localhost",
    "port": 5432
}

def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(url)[0]    
    df["Symbol"].to_csv("list_tickers.csv")
    tickers = df["Symbol"].tolist()    
    return tickers

def get_sp500_data():
    data_frames=[]
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        for asset in get_sp500_tickers():
            asset=asset.upper().replace(".","_")
            print(asset)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS sp500_{asset} (
                    time TIMESTAMPTZ PRIMARY KEY,
                    open DOUBLE PRECISION NULL,
                    high DOUBLE PRECISION NULL,
                    low_price DOUBLE PRECISION NULL,
                    close_price DOUBLE PRECISION NULL,
                    volume DOUBLE PRECISION NULL
                );
            """)
            conn.commit()
            try:
                asset_tracker = yf.Ticker(asset)
                history = asset_tracker.history(period="1y")  # Last 1 year
                print(history)

                if history.empty:
                    continue  # Skip assets with no data
                history = history.reset_index()  
                
                for index, row in history.iterrows():
                    cursor.execute(f"""INSERT INTO sp500_{asset} (time, open,high,low_price,close_price,volume)
                        VALUES ('{row["Date"]}', '{float(row["Open"])}', '{float(row["High"])}', '{float(row["Low"])}', '{float(row["Close"])}', '{float(row["Volume"])}')
                    """,)            
                history['Asset'] = asset  
                
                data_frames.append(history)

            except Exception as e:
                msg = str(e).lower()
                if "rate limited" in msg or "too many request" in msg:
                    print(f"[{asset}] Rate limited. Reintentando en {delay} segundos...")
                    time.sleep(delay)
                    delay *= 2  # backoff exponencial
                else:
                    print(f"[{asset}] Otro error: {e}")
                    break
  

        conn.commit()
        cursor.close()
        conn.close()
        print("Datos guardados en TimescaleDB.")

    except Exception as e:
        print("Error al insertar en TimescaleDB:", e)

    

    data_frames=pd.concat(data_frames,ignore_index=True)
    data_frames.to_csv("asda.csv")
    return data_frames

 

if __name__ == "__main__":
    while True:
        sp500_data = get_sp500_data()
        time.sleep(86400) 
