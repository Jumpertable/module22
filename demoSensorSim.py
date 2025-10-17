import paho.mqtt.client as mqtt
import time
import random

BROKER_ADDRESS = "broker.hivemq.com"
TOPIC = "char/sensor/temperature"
PUBLISH_INTERVAL = 5
TEMP_MIN = 20.0
TEMP_MAX = 30.0

client = mqtt.Client()
client.connect(BROKER_ADDRESS, 1883, 60)
client.loop_start()

try:
    time.sleep(1)
    while True:
        temperature = random.uniform(TEMP_MIN, TEMP_MAX)
        payload = f"{temperature:.2f}"
        client.publish(TOPIC, payload)
        print(f"Published Temperature: {payload}%")
        time.sleep(PUBLISH_INTERVAL)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()