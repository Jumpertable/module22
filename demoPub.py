import paho.mqtt.client as mqtt
import time

# --- Configuration ---
BROKER_ADDRESS = "broker.hivemq.com"
TOPIC = "char/counter_topic"
PUBLISH_INTERVAL = 3  # seconds

# --- Main Logic ---
client = mqtt.Client()
client.connect(BROKER_ADDRESS, 1883, 60)
client.loop_start()

counter = 0
try:
    time.sleep(1)
    while True:
        counter += 1
        payload = f"Count: {counter}"
        client.publish(TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(PUBLISH_INTERVAL)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()