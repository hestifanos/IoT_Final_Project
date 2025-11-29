import json
import sqlite3
from typing import Tuple, Optional

from pathlib import Path
import paho.mqtt.client as mqtt

# ---------- CONFIG ----------

# Project root = parent of the 'processor' folder
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "traffic.db"

print("Using database at:", DB_PATH)

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC       = "smart_traffic/intersection1"

FREE_FLOW_SPEED = 50.0          # km/h (adjustable)
ANOMALY_WINDOW  = 20            # number of previous samples
ANOMALY_DROP_FACTOR = 0.6       # 40% or more drop vs recent average


# ---------- DB HELPERS ----------

def ensure_tables_exist():
    """Create tables if they don't exist yet."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

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
    print("Tables ensured (traffic_samples, alerts).")


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def insert_sample(
    ts_utc: str,
    intersection_id: str,
    avg_speed: float,
    vehicle_count: int,
    congestion_score: float,
    congestion_level: str,
    is_anomaly: bool
):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO traffic_samples
        (ts_utc, intersection_id, avg_speed, vehicle_count,
         congestion_score, congestion_level, is_anomaly)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        ts_utc,
        intersection_id,
        avg_speed,
        vehicle_count,
        congestion_score,
        congestion_level,
        1 if is_anomaly else 0
    ))
    conn.commit()
    conn.close()


def insert_alert(ts_utc: str, intersection_id: str, message: str, severity: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO alerts (ts_utc, intersection_id, message, severity)
        VALUES (?, ?, ?, ?)
    """, (ts_utc, intersection_id, message, severity))
    conn.commit()
    conn.close()


def get_recent_avg_speed(intersection_id: str, limit: int) -> Optional[float]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT avg_speed
        FROM traffic_samples
        WHERE intersection_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (intersection_id, limit))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    speeds = [r[0] for r in rows]
    return sum(speeds) / len(speeds)


# ---------- LOGIC ----------

def compute_congestion(avg_speed: float) -> Tuple[float, str]:
    """Return (score, level). Score in [0,1], level = Green/Yellow/Orange/Red."""
    if avg_speed < 0:
        avg_speed = 0.0

    ratio = avg_speed / FREE_FLOW_SPEED if FREE_FLOW_SPEED > 0 else 0
    ratio = max(0.0, min(1.0, ratio))
    score = 1.0 - ratio

    if score < 0.25:
        level = "Green"
    elif score < 0.5:
        level = "Yellow"
    elif score < 0.75:
        level = "Orange"
    else:
        level = "Red"

    return score, level


def is_anomaly_speed_drop(intersection_id: str, current_speed: float) -> bool:
    recent_avg = get_recent_avg_speed(intersection_id, ANOMALY_WINDOW)
    if recent_avg is None or recent_avg <= 0:
        return False

    # If speed drops below 60% of recent average, treat as anomaly.
    return current_speed < (ANOMALY_DROP_FACTOR * recent_avg)


# ---------- MQTT CALLBACKS ----------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(TOPIC)
        print(f"Subscribed to topic: {TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        intersection_id = data.get("intersection_id", "intersection1")
        ts_utc = data.get("timestamp_utc")
        avg_speed = float(data.get("avg_speed_kmh", 0.0))
        vehicle_count = int(data.get("vehicle_count", 0))

        congestion_score, congestion_level = compute_congestion(avg_speed)
        anomaly = is_anomaly_speed_drop(intersection_id, avg_speed)

        insert_sample(
            ts_utc=ts_utc,
            intersection_id=intersection_id,
            avg_speed=avg_speed,
            vehicle_count=vehicle_count,
            congestion_score=congestion_score,
            congestion_level=congestion_level,
            is_anomaly=anomaly,
        )

        print(f"[{ts_utc}] speed={avg_speed:.1f} km/h "
              f"count={vehicle_count} level={congestion_level} "
              f"anomaly={anomaly}")

        if anomaly:
            message = (f"Sudden slowdown at {intersection_id}: "
                       f"{avg_speed:.1f} km/h vs recent trend.")
            insert_alert(
                ts_utc=ts_utc,
                intersection_id=intersection_id,
                message=message,
                severity="High"
            )
            print("ALERT:", message)

    except Exception as e:
        print("Error processing message:", e)


# ---------- MAIN ----------

def main():
    # Make sure DB + tables exist before subscribing
    ensure_tables_exist()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
