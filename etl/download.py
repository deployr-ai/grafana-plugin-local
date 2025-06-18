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
    data_frames = []
    delay = 1  # Initialize delay variable
    max_delay = 60  # Maximum delay of 60 seconds
    base_delay = 2  # Base delay between requests
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        tickers = get_sp500_tickers()
        
        print(f"Procesando {len(tickers)} empresas del S&P 500...")
        
        for i, asset in enumerate(tickers):
            original_asset = asset  # Keep original for yfinance
            asset_db = asset.upper().replace(".", "_")  # For database
            
            print(f"[{i+1}/{len(tickers)}] Procesando {asset}...")
            
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
            conn.commit()
            
            # Retry logic for rate limiting
            max_retries = 5
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    # Add base delay between requests to avoid immediate rate limiting
                    if retry_count == 0:  # Only on first attempt
                        time.sleep(base_delay)
                    
                    asset_tracker = yf.Ticker(original_asset)
                    history = asset_tracker.history(period="1y")  # Last 1 year

                    if history.empty:
                        print(f"[{asset}] No hay datos disponibles")
                        success = True  # Mark as success to avoid retries
                        break
                        
                    history = history.reset_index()  
                    
                    for index, row in history.iterrows():
                        cursor.execute(f"""INSERT INTO sp500_{asset_db} (time, open,high,low_price,close_price,volume)
                            VALUES ('{row["Date"]}', '{float(row["Open"])}', '{float(row["High"])}', '{float(row["Low"])}', '{float(row["Close"])}', '{float(row["Volume"])}')
                        """,)            
                        
                    history['Asset'] = original_asset  
                    data_frames.append(history)
                    
                    # Reset delay on successful request
                    delay = 1
                    success = True
                    print(f"[{asset}] ✓ Datos descargados exitosamente")

                except Exception as e:
                    msg = str(e).lower()
                    if "rate limited" in msg or "too many request" in msg:
                        retry_count += 1
                        # Cap the delay at max_delay
                        current_delay = min(delay, max_delay)
                        if retry_count < max_retries:
                            print(f"[{asset}] Rate limited. Reintento {retry_count}/{max_retries} en {current_delay} segundos...")
                            time.sleep(current_delay)
                            delay = min(delay * 2, max_delay)  # Don't exceed max_delay
                        else:
                            print(f"[{asset}]Rate limited - máximo de reintentos alcanzado")
                    else:
                        print(f"[{asset}] Error: {e}")
                        break  # Exit retry loop for non-rate-limit errors
  
        conn.commit()
        cursor.close()
        conn.close()
        print("Datos guardados en TimescaleDB.")

    except Exception as e:
        print("Error al insertar en TimescaleDB:", e)

    # Check if data_frames is empty before concatenating
    if data_frames:
        data_frames = pd.concat(data_frames, ignore_index=True)
        data_frames.to_csv("data_backup.csv")
        print("Datos guardados en data_backup.csv")
        return data_frames
    else:
        print("No se pudieron obtener datos para ningún activo.")
        return pd.DataFrame()  # Return empty DataFrame

if __name__ == "__main__":
    print("Iniciando descarga única de datos del S&P 500...")
    sp500_data = get_sp500_data()
    print("Proceso completado. El script ha terminado.")
    # Uncomment the lines below if you want it to run daily:
    # while True:
    #     sp500_data = get_sp500_data()
    #     time.sleep(86400)  # Sleep for 24 hours 