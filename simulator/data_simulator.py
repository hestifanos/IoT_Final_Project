import json
import time
import random
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC       = "smart_traffic/intersection1"

FREE_FLOW_SPEED = 50.0   
BASE_COUNT      = 10    


def generate_sample():
    """Generate synthetic speed & count with some random congestion behavior."""
    now = datetime.now(timezone.utc).isoformat()

    # Randomly simulate congestion bursts
    if random.random() < 0.2:
        avg_speed = random.uniform(5, 20)  # congested
        vehicle_count = random.randint(15, 30)
    else:
        avg_speed = random.uniform(35, 60)  # normal flow
        vehicle_count = random.randint(5, 20)

    return {
        "intersection_id": "intersection1",
        "timestamp_utc": now,
        "avg_speed_kmh": round(avg_speed, 2),
        "vehicle_count": vehicle_count,
    }


def main():
    client = mqtt.Client()
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    print(f"Publishing to MQTT {BROKER_HOST}:{BROKER_PORT}, topic={TOPIC}")
    try:
        while True:
            sample = generate_sample()
            payload = json.dumps(sample)
            result = client.publish(TOPIC, payload=payload, qos=0)
            status = result[0]
            if status == 0:
                print("Published:", payload)
            else:
                print("Failed to send message:", status)

            time.sleep(1)  
    except KeyboardInterrupt:
        print("Stopping simulator...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
