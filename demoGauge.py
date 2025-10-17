import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from queue import SimpleQueue

# --- MQTT Configuration ---
BROKER_ADDRESS = "broker.hivemq.com"
TOPIC = "char/sensor/humidity"

# --- Shared state ---
updates = SimpleQueue()   # thread-safe queue for new data

# ---------- Gauge Drawing ----------
MIN_VAL, MAX_VAL = 0.0, 100.0   # % scale

def draw_gauge(ax, value):
    v = max(MIN_VAL, min(MAX_VAL, value))
    ax.clear()
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Semicircle arc
    angles = np.linspace(-np.pi/2, np.pi/2, 200)
    ax.plot(angles, np.ones_like(angles)*0.9, color="lightgray", lw=16)

    # Ticks (every 10%)
    for t in np.linspace(MIN_VAL, MAX_VAL, 6):
        frac = (t - MIN_VAL) / (MAX_VAL - MIN_VAL)
        ang  = np.pi * (1 - frac) - np.pi/2
        ax.plot([ang, ang], [0.8, 0.92], color="black", lw=2)
        ax.text(ang, 0.72, f"{t:.0f}", ha="center", va="center", fontsize=9)

    # Needle
    frac = (v - MIN_VAL) / (MAX_VAL - MIN_VAL + 1e-12)
    ang  = np.pi * (1 - frac) - np.pi/2
    ax.plot([ang, ang], [0.0, 0.9], color="blue", lw=3)

    ax.set_title("Humidity Gauge (%)", fontsize=12, pad=20)

# ---------- Tkinter GUI ----------
root = tk.Tk()
root.title("MQTT Humidity Gauge")
root.geometry("520x520")

ttk.Label(root, text="Real-Time Humidity (MQTT)",
          font=("Arial", 14, "bold")).pack(pady=8)
value_label = ttk.Label(root, text="--.- °C", font=("Arial", 16))
value_label.pack(pady=8)

fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
draw_gauge(ax, MIN_VAL)
canvas.draw()

def apply_update():
    """Check for new data and refresh the gauge."""
    try:
        latest = None
        while True:
            latest = updates.get_nowait()
    except Exception:
        pass
    if latest is not None:
        value_label.config(text=f"{latest:.2f} °C")
        draw_gauge(ax, latest)
        canvas.draw()
    root.after(100, apply_update)

def on_close():
    try:
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# ---------- MQTT Callbacks ----------
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code: {rc}")
    if rc == 0:
        client.subscribe(TOPIC)
        print(f"Subscribed to: {TOPIC}")

def on_message(client, userdata, msg):
    try:
        temperature = float(msg.payload.decode())
        updates.put(temperature)
    except Exception:
        pass

# ---------- MQTT Setup ----------
client = mqtt.Client(
    client_id="TkGaugeSubscriber",
    callback_api_version=mqtt.CallbackAPIVersion.VERSION1
)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_ADDRESS, 1883, 60)
client.loop_start()

# Start GUI Loop
root.after(100, apply_update)
root.mainloop()

