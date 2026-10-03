import json
import time
import paho.mqtt.client as mqtt

# MQTT Settings
BROKER = "broker.hivemq.com"
PORT = 1883
TELEMETRY_TOPIC = "climasync/room101/telemetry"
CONTROL_TOPIC = "climasync/room101/control"

# Comfort & Energy Analytics Engine
def analyze_climate(data):
    temp = data.get("temperature", 24.0)
    humidity = data.get("humidity", 50.0)
    occupancy = data.get("occupancy", 0)

    # 1. Thermal Comfort Score % (Ideal: Temp 22-26 C, Hum 40-60%)
    temp_penalty = abs(temp - 24.0) * 8.0
    hum_penalty = abs(humidity - 50.0) * 1.2
    comfort_score = max(0.0, min(100.0, 100.0 - (temp_penalty + hum_penalty)))

    # 2. Optimal HVAC Setpoint (°C) based on Occupancy
    if occupancy == 1:
        optimal_setpoint = 23.0
        hvac_status = "ON"
    else:
        optimal_setpoint = 27.0  # Eco Mode
        hvac_status = "OFF" if temp <= 27.0 else "ON"

    # 3. Estimated Energy Savings %
    base_consumption = 2.5  # kW baseline
    actual_consumption = 1.2 if hvac_status == "OFF" or occupancy == 0 else 2.2
    energy_savings = round(((base_consumption - actual_consumption) / base_consumption) * 100, 1)

    return {
        "comfort_score": round(comfort_score, 1),
        "optimal_setpoint": optimal_setpoint,
        "hvac_status": hvac_status,
        "energy_savings": energy_savings
    }

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("==========================================")
    print(" ClimaSync Backend Analytics Service Running ")
    print("==========================================")
    print(f"Connected to HiveMQ Broker! Listening on: {TELEMETRY_TOPIC}\n")
    client.subscribe(TELEMETRY_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"📥 Received Sensor Telemetry: {payload}")

        # Process Analytics
        analytics = analyze_climate(payload)

        print(f"   📊 Comfort Score: {analytics['comfort_score']}%")
        print(f"   🎯 Optimal HVAC Setpoint: {analytics['optimal_setpoint']} °C")
        print(f"   ⚡ Estimated Energy Savings: {analytics['energy_savings']}%")
        print(f"   🕹️ Triggering HVAC Relay: {analytics['hvac_status']}")

        # Publish Control Action back to Wokwi ESP32
        client.publish(CONTROL_TOPIC, analytics['hvac_status'])
        print("------------------------------------------\n")

    except Exception as e:
        print(f"Error processing message: {e}")

# Main
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()