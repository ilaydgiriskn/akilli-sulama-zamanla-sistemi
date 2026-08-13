import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'sulama.db')

def get_connection():
    """SQLite veritabanı bağlantısı oluşturur ve döner."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Veritabanı tablolarını oluşturur."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # parcel tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parcel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            crop_type TEXT NOT NULL,
            crop_growth_stage TEXT NOT NULL,
            season TEXT NOT NULL,
            mulching_used TEXT NOT NULL,
            soil_moisture REAL NOT NULL,
            soil_ph REAL NOT NULL,
            soil_type TEXT NOT NULL
        )
    ''')
    
    # irrigation_record tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS irrigation_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parcel_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            decision TEXT NOT NULL,
            temperature_max REAL,
            precipitation REAL,
            FOREIGN KEY (parcel_id) REFERENCES parcel (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_parcel(name, latitude, longitude, crop_type, crop_growth_stage, season, mulching_used, soil_moisture, soil_ph, soil_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO parcel (name, latitude, longitude, crop_type, crop_growth_stage, season, mulching_used, soil_moisture, soil_ph, soil_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, latitude, longitude, crop_type, crop_growth_stage, season, mulching_used, soil_moisture, soil_ph, soil_type))
    parcel_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return parcel_id

def get_all_parcels():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM parcel')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_parcel(parcel_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM parcel WHERE id = ?', (parcel_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None



def add_irrigation_record(parcel_id, date, decision, temp_max, precipitation):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO irrigation_record (parcel_id, date, decision, temperature_max, precipitation)
        VALUES (?, ?, ?, ?, ?)
    ''', (parcel_id, date, decision, temp_max, precipitation))
    conn.commit()
    conn.close()

def get_irrigation_history(parcel_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM irrigation_record WHERE parcel_id = ? ORDER BY date DESC
    ''', (parcel_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
    print("Veritabanı tabloları başarıyla oluşturuldu.")
