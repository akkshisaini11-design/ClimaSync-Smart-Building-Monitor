import streamlit as st
import json
import time
import paho.mqtt.client as mqtt
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ClimaSync Dashboard", layout="wide")

st.title("🌡️ ClimaSync: Smart Building Environmental Dashboard")
st.markdown("Real-time IoT Telemetry & Analytics Platform")

# State Initialization
if 'telemetry' not in st.session_state:
    st.session_state.telemetry = {"temperature": 24.0, "humidity": 40.0, "occupancy": 0}

if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Time", "Temperature", "Humidity"])

# Callback for MQTT
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        st.session_state.telemetry = data
        new_row = pd.DataFrame([{
            "Time": time.strftime("%H:%M:%S"),
            "Temperature": data.get("temperature", 24.0),
            "Humidity": data.get("humidity", 40.0)
        }])
        st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(20)
    except Exception as e:
        pass

# MQTT Setup
@st.cache_resource
def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.subscribe("climasync/room101/telemetry")
    client.loop_start()
    return client

start_mqtt()

# Metrics Display
temp = st.session_state.telemetry.get("temperature", 24.0)
hum = st.session_state.telemetry.get("humidity", 40.0)
occ = "Occupied" if st.session_state.telemetry.get("occupancy", 0) == 1 else "Vacant"

# Analytics Calculations
temp_penalty = abs(temp - 24.0) * 8.0
hum_penalty = abs(hum - 50.0) * 1.2
comfort_score = max(0.0, min(100.0, 100.0 - (temp_penalty + hum_penalty)))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Temperature (°C)", f"{temp} °C")
col2.metric("Humidity (%)", f"{hum} %")
col3.metric("Room Occupancy", occ)
col4.metric("Thermal Comfort Score", f"{round(comfort_score, 1)}%")

st.divider()

# Charts
c1, c2 = st.columns(2)

with c1:
    st.subheader("Live Temperature & Humidity Trends")
    if not st.session_state.history.empty:
        fig = px.line(st.session_state.history, x="Time", y=["Temperature", "Humidity"], markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Waiting for telemetry data...")

with c2:
    st.subheader("HVAC Control & Efficiency")
    st.write(f"**Optimal Setpoint:** {'23.0 °C (Active Cooling)' if occ == 'Occupied' else '27.0 °C (Eco Mode)'}")
    st.write(f"**HVAC Status:** {'RUNNING' if occ == 'Occupied' or temp > 27.0 else 'IDLE / OFF'}")
    st.write(f"**Estimated Energy Savings:** {30.0 if occ == 'Vacant' else 12.0}%")

time.sleep(2)
st.rerun()