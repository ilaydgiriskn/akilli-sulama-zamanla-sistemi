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
            water_budget REAL DEFAULT 0.0
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

def add_parcel(name, latitude, longitude, crop_type, water_budget=0.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO parcel (name, latitude, longitude, crop_type, water_budget)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, latitude, longitude, crop_type, water_budget))
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

def update_water_budget(parcel_id, new_budget):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE parcel SET water_budget = ? WHERE id = ?
    ''', (new_budget, parcel_id))
    conn.commit()
    conn.close()

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
