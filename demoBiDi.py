import paho.mqtt.client as mqtt
import time, random, json

# --- MQTT Configuration ---
BROKER = "broker.hivemq.com"
PUB_TOPIC = "charlotte/sensor/temperature"
SUB_TOPIC = "device/control/state"

# --- Callback: Connection Established ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker successfully.")
        client.subscribe(SUB_TOPIC)
        print(f"📡 Subscribed to topic: {SUB_TOPIC}")
    else:
        print(f"❌ Connection failed with code {rc}")

# --- Callback: Message Received ---
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"📥 Received from {msg.topic}: {payload}")

        # Try to parse JSON payload (if structured control command)
        try:
            data = json.loads(payload)
            if "state" in data:
                state = data["state"]
                print(f"🟢 Device Command: State set to {state}")
        except json.JSONDecodeError:
            print("⚠️ Non-JSON message received.")

    except Exception as e:
        print(f"Error processing message: {e}")

# --- Initialize Client ---
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)
client.loop_start()

# --- Main Loop: Publish Temperature ---
try:
    while True:
        temperature = round(random.uniform(20.0, 30.0), 2)
        client.publish(PUB_TOPIC, str(temperature))
        print(f"🌡️ Published Temperature: {temperature} °C")
        time.sleep(5)

except KeyboardInterrupt:
    print("\n🛑 KeyboardInterrupt detected, disconnecting...")
    client.loop_stop()
    client.disconnect()
    print("🔌 Disconnected from MQTT broker.")
