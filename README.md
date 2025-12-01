Smart Traffic Mini
Real-Time IoT Traffic Monitoring Prototype

Smart Traffic Mini is a lightweight real-time traffic monitoring system that simulates an intelligent intersection using IoT-style sensor data. It demonstrates how cities can use live data streams, analytics, and dashboards to understand congestion, detect anomalies, and visualize traffic conditions.

The system simulates traffic at the Conlin Rd & Simcoe St N intersection in Oshawa (Ontario Tech North Campus) and provides:

Real-time vehicle speed and vehicle count

Automatic congestion level scoring

Sudden slowdown (anomaly) detection

A live dashboard with charts and maps

An embedded Google Maps view of the real intersection

Everything runs locally on one laptop with no cloud services required.

System Architecture
Data Simulator → MQTT Broker → Processor → SQLite DB → Streamlit Dashboard

Components Overview
Component	Technology	Purpose
Data Simulator	Python + MQTT	Generates synthetic traffic data every second
Message Broker	Mosquitto (Docker)	Delivers live MQTT messages
Processor	Python	Computes congestion score, detects anomalies, writes to database
Database	SQLite	Stores recent traffic readings (auto-created)
Dashboard	Streamlit + PyDeck	Displays charts, status panel, and map
Key Features

Real-time updates every few seconds

Simulated vehicle speed and flow

Congestion levels: Green, Yellow, Orange, Red

Sudden-slowdown anomaly detection

Interactive map and Google Maps embed

Runs on Linux, macOS, or Windows

Lightweight and ideal for demos and student labs

How to Run the Project (Step-by-Step)
1. Set up the environment
cd ~/Documents/smart_traffic_mini

python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

pip install -r requirements.txt

2. Start the MQTT Broker (Docker)

Terminal 1:

cd ~/Documents/smart_traffic_mini
docker run -it -p 1883:1883 eclipse-mosquitto


Keep this terminal open.

3. Start the Data Simulator

Terminal 2:

cd ~/Documents/smart_traffic_mini
source .venv/bin/activate

cd simulator
python3 data_simulator.py


You will see output like:

Publishing to MQTT localhost:1883, topic=smart_traffic/intersection1
{"avg_speed_kmh": 45.2, "vehicle_count": 12, ...}

4. Start the Processor (analytics + database)

Terminal 3:

cd ~/Documents/smart_traffic_mini
source .venv/bin/activate

cd processor
python3 processor.py


Sample output:

Using database at: traffic.db
Connected to MQTT broker
speed=54.1 km/h, count=18, level=Green, anomaly=False

5. Start the Dashboard

Terminal 4:

cd ~/Documents/smart_traffic_mini
source .venv/bin/activate

cd dashboard
streamlit run dashboard.py


Streamlit will show a link:

http://localhost:8501


Open it in your browser.

What You Will See

A status card showing current congestion level

Real-time speed and vehicle count

Line charts for speed and flow over time

A simple simulation map

An embedded Google Maps view of the Conlin & Simcoe intersection

Project Structure
smart_traffic_mini/
  - simulator/
    - data_simulator.py
  - processor/
    - processor.py
  - dashboard/
    - dashboard.py
  - traffic.db
  - requirements.txt
  -  README.md

Conclusion

Smart Traffic Mini demonstrates how MQTT streaming, real-time analytics, and dashboards can work together to monitor traffic at a single intersection. It is simple enough for classroom demonstrations, yet structured so it can be expanded to support multiple intersections, cloud hosting, or real sensor inputs in future development.