import sqlite3
import requests
import time

DB_FILE = "smjp_gios_polska.db"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
ALLOWED_PARAMETERS = {'PM10', 'PM2.5', 'O3', 'NO2', 'SO2', 'C6H6', 'CO'}

def init_database():
    print("Inicjalizacja struktur bazy danych...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stations (
        id INTEGER PRIMARY KEY, station_code TEXT NOT NULL, name TEXT NOT NULL,
        latitude REAL NOT NULL, longitude REAL NOT NULL, city_name TEXT NOT NULL,
        province TEXT NOT NULL, street TEXT
    );""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensors (
        id INTEGER PRIMARY KEY, station_id INTEGER NOT NULL, param_name TEXT NOT NULL,
        param_code TEXT NOT NULL, param_formula TEXT NOT NULL,
        FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE
    );""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT, sensor_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL, value REAL,
        UNIQUE(sensor_id, timestamp),
        FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE
    );""")
      
    #Tabela Użytkowników

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        newsletter_opt_in INTEGER DEFAULT 0, -- 0 = Nie, 1 = Tak (Wymóg RODO)
        last_login_at TEXT,                  -- Do analityki aktywności użytkowników
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );""")

    #Tabela Ulubionych Stacji 

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS favorite_stations (
        user_id INTEGER NOT NULL,
        station_id INTEGER NOT NULL,
        custom_alias TEXT,                   -- np. 'Dom', 'Biuro', 'Przedszkole bombelka'
        added_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, station_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE);""")

  
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meas_sensor_time ON measurements(sensor_id, timestamp);")


    # Normy jakości powietrza (Tabela aqi_norms)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aqi_norms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        param_code TEXT NOT NULL,
        index_level TEXT NOT NULL,
        min_value REAL NOT NULL,
        max_value REAL NOT NULL,
        color_hex TEXT NOT NULL
    );""")
    
    # Wypełnienie norm, jeśli tabela jest pusta
    cursor.execute("SELECT COUNT(*) FROM aqi_norms")
    if cursor.fetchone()[0] == 0:
        aqi_norms_data = [
            ('PM10', 'Bardzo dobry', 0, 20, '#50B748'), ('PM10', 'Dobry', 20.1, 50, '#B0D235'), ('PM10', 'Umiarkowany', 50.1, 80, '#F8C300'), ('PM10', 'Dostateczny', 80.1, 110, '#F27921'), ('PM10', 'Zły', 110.1, 150, '#E2001A'), ('PM10', 'Bardzo zły', 150.1, 9999, '#8A0E1A'),
            ('PM2.5', 'Bardzo dobry', 0, 13, '#50B748'), ('PM2.5', 'Dobry', 13.1, 35, '#B0D235'), ('PM2.5', 'Umiarkowany', 35.1, 55, '#F8C300'), ('PM2.5', 'Dostateczny', 55.1, 75, '#F27921'), ('PM2.5', 'Zły', 75.1, 110, '#E2001A'), ('PM2.5', 'Bardzo zły', 110.1, 9999, '#8A0E1A'),
            ('O3', 'Bardzo dobry', 0, 70, '#50B748'), ('O3', 'Dobry', 70.1, 120, '#B0D235'), ('O3', 'Umiarkowany', 120.1, 150, '#F8C300'), ('O3', 'Dostateczny', 150.1, 180, '#F27921'), ('O3', 'Zły', 180.1, 240, '#E2001A'), ('O3', 'Bardzo zły', 240.1, 9999, '#8A0E1A'),
            ('NO2', 'Bardzo dobry', 0, 40, '#50B748'), ('NO2', 'Dobry', 40.1, 100, '#B0D235'), ('NO2', 'Umiarkowany', 100.1, 150, '#F8C300'), ('NO2', 'Dostateczny', 150.1, 230, '#F27921'), ('NO2', 'Zły', 230.1, 400, '#E2001A'), ('NO2', 'Bardzo zły', 400.1, 9999, '#8A0E1A'),
            ('SO2', 'Bardzo dobry', 0, 50, '#50B748'), ('SO2', 'Dobry', 50.1, 100, '#B0D235'), ('SO2', 'Umiarkowany', 100.1, 200, '#F8C300'), ('SO2', 'Dostateczny', 200.1, 350, '#F27921'), ('SO2', 'Zły', 350.1, 500, '#E2001A'), ('SO2', 'Bardzo zły', 500.1, 9999, '#8A0E1A')
        ]
        cursor.executemany("INSERT INTO aqi_norms (param_code, index_level, min_value, max_value, color_hex) VALUES (?, ?, ?, ?, ?)", aqi_norms_data)
    
    conn.commit()
    conn.close()

def load_history():
    print("\n--- POBIERANIE PEŁNEJ HISTORII DLA POLSKI ---")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    all_stations = []
    page = 0
    total_pages = 1
    
    while page < total_pages:
        try:
            res = requests.get(f"https://api.gios.gov.pl/pjp-api/v1/rest/station/findAll?page={page}&size=50", headers=HEADERS, timeout=15)
            if res.status_code == 200:
                data = res.json()
                total_pages = data.get('totalPages', 1)
                all_stations.extend(data.get('Lista stacji pomiarowych', []))
                page += 1
            else:
                break
        except: break
            
    total_stations = len(all_stations)
    print(f"Zapisywanie {total_stations} stacji...")

    for current_index, station_data in enumerate(all_stations):
        station_id = station_data['Identyfikator stacji']
        print(f"[{current_index + 1}/{total_stations}] {station_data['Nazwa stacji']}")
        
        cursor.execute("""
        INSERT OR REPLACE INTO stations (id, station_code, name, latitude, longitude, city_name, province, street)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (station_id, station_data['Kod stacji'], station_data['Nazwa stacji'], station_data['WGS84 φ N'], station_data['WGS84 λ E'], station_data.get('Nazwa miasta', 'Nieznane'), station_data['Województwo'], station_data.get('Ulica')))

        try:
            sensors_res = requests.get(f"https://api.gios.gov.pl/pjp-api/v1/rest/station/sensors/{station_id}", headers=HEADERS, timeout=15)
            if sensors_res.status_code != 200: continue
            sensors_data = sensors_res.json()
            sensors_list = []
            
            if isinstance(sensors_data, dict):
                list_key = [k for k in sensors_data.keys() if 'stanowisk' in k.lower() or 'czujnik' in k.lower() or 'Lista' in k]
                if list_key: sensors_list = sensors_data.get(list_key[0], [])
            elif isinstance(sensors_data, list):
                sensors_list = sensors_data
                
            for sensor in sensors_list:
                sensor_id = sensor.get('Identyfikator stanowiska') or sensor.get('id')
                param_code = sensor.get('Wskaźnik - kod') or sensor.get('param', {}).get('paramCode', 'UNKNOWN')
                
                if not sensor_id: continue
                
                if param_code not in ALLOWED_PARAMETERS:
                    continue
                
                cursor.execute("""
                INSERT OR REPLACE INTO sensors (id, station_id, param_name, param_code, param_formula)
                VALUES (?, ?, ?, ?, ?)
                """, (sensor_id, station_id, sensor.get('Wskaźnik', 'Brak'), param_code, sensor.get('Wskaźnik - wzór', 'Brak')))
                
                data_res = requests.get(f"https://api.gios.gov.pl/pjp-api/v1/rest/data/getData/{sensor_id}", headers=HEADERS, timeout=15)
                if data_res.status_code == 200:
                    meas_json = data_res.json()
                    values = []
                    if isinstance(meas_json, dict):
                        for val in meas_json.values():
                            if isinstance(val, list): values = val; break
                    elif isinstance(meas_json, list): values = meas_json
                        
                    saved_count = 0
                    for val in values:
                        m_val, m_date = None, None
                        for k, v in val.items():
                            if 'val' in k.lower() or 'wart' in k.lower(): m_val = v
                            elif 'dat' in k.lower() or 'czas' in k.lower(): m_date = v
                        
                        if m_val is not None and m_date is not None:
                            cursor.execute("INSERT OR IGNORE INTO measurements (sensor_id, timestamp, value) VALUES (?, ?, ?)", (sensor_id, m_date, m_val))
                            if cursor.rowcount > 0: saved_count += 1
                    if saved_count > 0: print(f"  -> Zapisano {saved_count} odczytów z historii ({param_code}).")
                time.sleep(0.1)
        except: pass
        conn.commit()
    conn.close()
    print("\nGOTOWE! Zbudowano bazę i archiwum.")

if __name__ == "__main__":
    init_database()
    load_history()