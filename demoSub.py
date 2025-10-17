import paho.mqtt.client as mqtt
import time

# --- Configuration ---
BROKER_ADDRESS = "broker.hivemq.com"
TOPIC = "char/counter_topic"
SUB_TOPIC = "device/control/state"

# --- Callback Functions ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)
        print(f"🔔 Subscribed to topic: {TOPIC}")

def on_message(client, userdata, msg):
    print(f"➡️ Received: [Topic: {msg.topic}] {msg.payload.decode()}")

# --- Main Logic ---
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_ADDRESS, 1883, 60)

try:
    print("🚀 Starting client loop. Press Ctrl+C to stop.")
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()