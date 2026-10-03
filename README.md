# 🌡️ ClimaSync: Smart Building Environmental & Energy Management Platform

ClimaSync is an end-to-end IoT and Data Analytics application that monitors indoor microclimate metrics (Temperature, Humidity, Occupancy) via ESP32 telemetry, calculates thermal comfort scores, and triggers dynamic HVAC control logic.

## 🚀 Architecture
- **IoT Firmware / Simulation:** ESP32, DHT22, PIR Sensor, Relay Module simulated via Wokwi.
- **Protocol:** MQTT via HiveMQ Broker (`climasync/room101/telemetry` & `control`).
- **Analytics Engine:** Python Backend for Thermal Comfort Index (%) & Energy Savings estimation.
- **Dashboard:** Interactive Streamlit Web Interface with Live Plotly Data Visualization.

## 🛠️ How to Run
1. Start Wokwi Simulation (`sketch.ino`).
2. Run Analytics Engine:
   ```bash
   python backend.py