from pathlib import Path
import sqlite3

# Project root directory 
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "traffic.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Main traffic samples table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS traffic_samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts_utc TEXT NOT NULL,
        intersection_id TEXT NOT NULL,
        avg_speed REAL NOT NULL,
        vehicle_count INTEGER NOT NULL,
        congestion_score REAL NOT NULL,
        congestion_level TEXT NOT NULL,
        is_anomaly INTEGER NOT NULL CHECK (is_anomaly IN (0,1))
    );
    """)

    # Alerts table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts_utc TEXT NOT NULL,
        intersection_id TEXT NOT NULL,
        message TEXT NOT NULL,
        severity TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
    print("Database initialized at:", DB_PATH)


if __name__ == "__main__":
    init_db()
