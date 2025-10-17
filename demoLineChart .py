import tkinter as tk
from tkinter import ttk
import time
from collections import deque
from queue import SimpleQueue
import matplotlib.dates as mdates
from datetime import datetime

import paho.mqtt.client as mqtt
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- MQTT Config ---
BROKER_ADDRESS = "broker.hivemq.com"
TOPIC = "char/sensor/temperature"   # must match your publisher

# --- Data/State ---
MAX_POINTS = 300            # keep last N points (~5 min if publisher=1s)
values = deque(maxlen=MAX_POINTS)
timestamps = deque(maxlen=MAX_POINTS)
updates = SimpleQueue()     # thread-safe handoff MQTT -> GUI

# ---------- Tkinter GUI ----------
root = tk.Tk()
root.title("MQTT Temperature — Live Line Chart")
root.geometry("820x560")

title = ttk.Label(root, text="Real-Time Temperature (MQTT)", font=("Arial", 14, "bold"))
title.pack(pady=(10, 4))

stats_label = ttk.Label(root, text="Min: --  Max: --  Avg: --", font=("Arial", 11))
stats_label.pack(pady=(0, 8))

# Matplotlib figure
fig, ax = plt.subplots(figsize=(8, 4))
line, = ax.plot([], [], lw=2)
ax.set_title("Temperature vs Time")
ax.set_xlabel("Samples (most recent on the right)")
ax.set_ylabel("Temperature (°C)")
ax.grid(True, alpha=0.3)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# ---------- Plot update ----------
def refresh_plot():
    """Pull the latest values from the queue, update data arrays and redraw chart."""
    # Drain the queue to get the newest reading
    latest = None
    try:
        while True:
            latest = updates.get_nowait()  # (t, value)
    except Exception:
        pass

    if latest is not None:
        t, v = latest
        timestamps.append(t)
        values.append(v)

        # Update line
        x = list(range(len(values)))  # simple sample index on x-axis
        line.set_data(x, list(values))
        if values:
            ax.set_xlim(0, max(10, len(values)-1))
            ymin = min(values)
            ymax = max(values)
            pad = max(0.5, (ymax - ymin) * 0.1)
            ax.set_ylim(ymin - pad, ymax + pad)

            # Stats
            avg = sum(values) / len(values)
            stats_label.config(text=f"Min: {ymin:.2f}  Max: {ymax:.2f}  Avg: {avg:.2f}")

        canvas.draw_idle()

    # Schedule again
    root.after(200, refresh_plot)  # ~5 Hz UI refresh

def on_close():
    try:
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# ---------- MQTT callbacks ----------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected successfully to MQTT broker with result code {rc}")
        client.subscribe(TOPIC)
        print(f"🔔 Subscribed to topic: {TOPIC}")
    else:
        print(f"❌ Connection failed with result code {rc}")

def on_message(client, userdata, msg):
    try:
        val = float(msg.payload.decode())
        updates.put((time.time(), val))  # pass timestamp + value to GUI thread
    except ValueError:
        print(f"Error: Received non-numeric data on {msg.topic}: {msg.payload.decode()}")

# ---------- MQTT setup (paho-mqtt 2.x safe) ----------
# Use legacy callback API v1 so current callback signatures work unchanged.
client = mqtt.Client(
    client_id="TkLineChartSubscriber",
    callback_api_version=mqtt.CallbackAPIVersion.VERSION1
)
client.on_connect = on_connect
client.on_message = on_message

print(f"Attempting to connect to {BROKER_ADDRESS}...")
client.connect(BROKER_ADDRESS, 1883, 60)
client.loop_start()

# Start GUI
root.after(200, refresh_plot)
root.mainloop()