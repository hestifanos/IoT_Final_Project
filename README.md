Copy everything inside this box into your README.md file:

#  Smart Traffic Mini  
### Real-Time IoT Traffic Monitoring Prototype

The **Smart Traffic Mini** is a lightweight real-time traffic monitoring system that simulates an intelligent intersection using IoT-style sensor data. It demonstrates how cities can use live data pipelines, analytics, and dashboards to track congestion, detect anomalies, and visualize traffic conditions.

The project simulates vehicle flow at the **Conlin Rd & Simcoe St N intersection in Oshawa** (Ontario Tech North Campus area) and provides:

- Real-time vehicle speed & count  
- Automatic congestion scoring  
- Anomaly (sudden slowdown) detection  
- Live visualization via an interactive dashboard  
- A real Google Maps embed for the actual intersection

Everything runs **locally** on one laptop — no cloud servers required.

---

##  System Architecture

```text
Data Simulator → MQTT Broker → Processor → SQLite DB → Streamlit Dashboard

Components Overview
Component	Technology	Purpose
Data Simulator	Python + MQTT	Generates fake traffic sensor data (speed, vehicle count) every second
Message Broker	Mosquitto (Docker)	Handles live MQTT message delivery
Processor	Python	Computes congestion score, detects anomalies, and stores data
Database	SQLite	Stores recent samples & metadata; no setup required
Dashboard	Streamlit + PyDeck	Real-time charts, status card, simulated map, and embedded Google Maps
 Key Features

 Real-time updates every few seconds

 Simulated vehicle speed & flow at an intersection

 Congestion scoring: Green, Yellow, Orange, Red

 Sudden-slowdown anomaly detection

 Interactive live map + real Google Maps embed

 Runs entirely locally on Linux/Mac/Windows

 Extremely lightweight — perfect for demos & student projects

 How to Run the Project (Step-By-Step)

Below are the exact commands to run Smart Traffic Mini.

1 Set up the environment
# Go to project folder
cd ~/Documents/smart_traffic_mini

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

2 Start the MQTT Broker (Docker)

In Terminal 1:

cd ~/Documents/smart_traffic_mini

docker run -it -p 1883:1883 eclipse-mosquitto


Keep this terminal running.

3 Start the Data Simulator

In Terminal 2:

cd ~/Documents/smart_traffic_mini
source .venv/bin/activate

cd simulator
python3 data_simulator.py


You should see lines like:

Publishing to MQTT localhost:1883, topic=smart_traffic/intersection1
{"avg_speed_kmh": 45.2, "vehicle_count": 12, ...}


Keep this terminal running.

4 Start the Processor (analytics + SQLite)

In Terminal 3:

cd ~/Documents/smart_traffic_mini
source .venv/bin/activate

cd processor
python3 processor.py


Typical output:

Using database at: /path/to/traffic.db
Connected to MQTT broker
speed=54.1 km/h, count=18, level=Green, anomaly=False


Keep this terminal running.

5 Start the Dashboard (Streamlit)

In Terminal 4:

cd ~/Documents/smart_traffic_mini
source .venv/bin/activate

cd dashboard
streamlit run dashboard.py


Streamlit will show a URL like:

  Local URL: http://localhost:8501


Open that URL in your browser.

 What You Will See

A color-coded status card

Current speed, vehicles/sec, congestion level, anomaly flag

Speed over Time and Vehicle Count over Time charts

Live simulation map showing congestion at Conlin & Simcoe

Embedded Google Maps view of the real intersection

 Project Structure
smart_traffic_mini/
├── simulator/
│   └── data_simulator.py
├── processor/
│   └── processor.py
├── dashboard/
│   └── dashboard.py
├── traffic.db          # auto-created
├── requirements.txt
└── README.md

✔ Conclusion

Smart Traffic Mini demonstrates how IoT-style streaming, MQTT, real-time analytics, and dashboards can work together to monitor traffic at a single urban intersection. It is simple enough for classroom demos but structured so it can be extended to multiple intersections or cloud deployment in future work.

::contentReference[oaicite:0]{index=0}
