import tkinter as tk
from tkinter import ttk
import threading
import time
import RPi.GPIO as GPIO
import datetime

# GPIO Pin Assignments
m1, m2, m3, m4 = 40, 38, 36, 32
firepin = 11
metalpin = 12
buzzerpin = 13

# GPIO Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup([m1, m2, m3, m4, buzzerpin], GPIO.OUT, initial=0)
GPIO.setup(firepin, GPIO.IN)
GPIO.setup(metalpin, GPIO.IN)

def buzzering():
    GPIO.output(buzzerpin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(buzzerpin, GPIO.LOW)

def stoprobo():
    GPIO.output(m1, GPIO.LOW)
    GPIO.output(m2, GPIO.LOW)
    GPIO.output(m3, GPIO.LOW)
    GPIO.output(m4, GPIO.LOW)

def forwardrobo():
    GPIO.output(m1, GPIO.HIGH)
    GPIO.output(m2, GPIO.LOW)
    GPIO.output(m3, GPIO.HIGH)
    GPIO.output(m4, GPIO.LOW)

def backwardrobo():
    GPIO.output(m1, GPIO.LOW)
    GPIO.output(m2, GPIO.HIGH)
    GPIO.output(m3, GPIO.LOW)
    GPIO.output(m4, GPIO.HIGH)

def leftrobo():
    GPIO.output(m1, GPIO.HIGH)
    GPIO.output(m2, GPIO.LOW)
    GPIO.output(m3, GPIO.LOW)
    GPIO.output(m4, GPIO.LOW)

def rightrobo():
    GPIO.output(m1, GPIO.LOW)
    GPIO.output(m2, GPIO.LOW)
    GPIO.output(m3, GPIO.HIGH)
    GPIO.output(m4, GPIO.LOW)

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("robot_logs.txt", "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    log_text.config(state='normal')
    # Add color for fire detection
    if "🔥" in message:
        log_text.insert(tk.END, f"[{timestamp}] {message}\n", 'fire')
    else:
        log_text.insert(tk.END, f"[{timestamp}] {message}\n")
    log_text.see(tk.END)
    log_text.config(state='disabled')

def update_sensors():
    while True:
        fireval = GPIO.input(firepin)
        if fireval == 0:
            fire_label.config(text="🔥 FIRE DETECTED!", fg="red")
            log_event("🔥 Fire Detected")
            buzzering()
        else:
            fire_label.config(text="🔥 Fire Sensor: NORMAL", fg="white")

        metalval = GPIO.input(metalpin)
        if metalval == 0:
            metal_label.config(text="💣 Land Mine Detected!", fg="red")
            log_event("💣 Land Mine Detected")
            buzzering()
        else:
            metal_label.config(text="🧲 Metal Sensor: NORMAL", fg="white")

        time.sleep(1)

def move_robot(direction):
    status_label.config(text=f"Moving {direction}")
    execute_command(direction)

def stop_robot():
    status_label.config(text="Stopped")
    execute_command("Stop")

def execute_command(command):
    if command == "Forward":
        forwardrobo()
    elif command == "Stop":
        stoprobo()
    elif command == "Left":
        leftrobo()
    elif command == "Right":
        rightrobo()
    elif command == "Backward":
        backwardrobo()

# GUI
root = tk.Tk()
root.title("Robot Control Panel")
root.geometry("500x600")
root.configure(bg="black")

tk.Label(root, text="🤖 Robot Control Panel", font=("Arial", 18, "bold"), bg="black", fg="#00ffcc").pack(pady=10)

btn_style = {"font": ("Arial", 12, "bold"), "fg": "white", "bg": "#444", "width": 10, "height": 2}
label_style = {"font": ("Arial", 14), "fg": "white", "bg": "black"}

btn_frame = tk.Frame(root, bg="black")
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Forward", command=lambda: move_robot("Forward"), **btn_style).grid(row=0, column=1)
tk.Button(btn_frame, text="Left", command=lambda: move_robot("Left"), **btn_style).grid(row=1, column=0)
tk.Button(btn_frame, text="Stop", command=stop_robot, **btn_style).grid(row=1, column=1)
tk.Button(btn_frame, text="Right", command=lambda: move_robot("Right"), **btn_style).grid(row=1, column=2)
tk.Button(btn_frame, text="Backward", command=lambda: move_robot("Backward"), **btn_style).grid(row=2, column=1)

fire_label = tk.Label(root, text="🔥 Fire Sensor: Waiting...", **label_style)
fire_label.pack(pady=5)

metal_label = tk.Label(root, text="🧲 Metal Sensor: Waiting...", **label_style)
metal_label.pack(pady=5)

battery_frame = tk.Frame(root, bg="black")
battery_frame.pack(pady=5, anchor='e', padx=10)

tk.Label(battery_frame, text="Battery:", fg="white", bg="black", font=("Arial", 10)).pack(side='left')
battery_bar = ttk.Progressbar(battery_frame, length=120, mode='determinate')
battery_bar.pack(side='left')
battery_bar['value'] = 94
battery_percent = tk.Label(battery_frame, text="94%", fg="white", bg="black", font=("Arial", 10))
battery_percent.pack(side='left', padx=5)

# Log Frame with Scrollbar
log_frame = tk.Frame(root)
log_frame.pack(pady=10)
log_text = tk.Text(log_frame, height=10, width=58, bg="#222", fg="lime", font=("Courier", 10), wrap=tk.WORD)
scrollbar = ttk.Scrollbar(log_frame, command=log_text.yview)
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_text.config(yscrollcommand=scrollbar.set, state='disabled')
log_text.tag_configure('fire', foreground='red')  # Configure fire text color

status_label = tk.Label(root, text="Status: Idle", **label_style)
status_label.pack(pady=10)

def on_key_press(event):
    key = event.keysym.lower()
    if key == "up":
        move_robot("Forward")
    elif key == "down":
        move_robot("Backward")
    elif key == "left":
        move_robot("Left")
    elif key == "right":
        move_robot("Right")
    elif key == "space":
        stop_robot()

root.bind("<Up>", on_key_press)
root.bind("<Down>", on_key_press)
root.bind("<Left>", on_key_press)
root.bind("<Right>", on_key_press)
root.bind("<space>", on_key_press)

sensor_thread = threading.Thread(target=update_sensors, daemon=True)
sensor_thread.start()

root.mainloop()
