import cv2
import time
import threading
from collections import defaultdict
from ultralytics import YOLO
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import queue

# Load YOLO model
model = YOLO("best.pt")
class_labels = model.names
min_duration = 5  # seconds to confirm detection
detections = defaultdict(lambda: {"start_time": None, "confirmed": False})
log_queue = queue.Queue()

# Add log to GUI queue
def log_event(message, tag=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    log_queue.put((full_message, tag))
    with open("pred_logs.txt", "a") as f:
        f.write(full_message + "\n")

# Popup handler (thread-safe)
def show_popup(label):
    def ask():
        result = messagebox.askyesno("⚠️ Target Detected", f"{label} detected.\nDo you want to launch missile?")
        if result:
            log_event(f"🚀 Missile Launched at {label}", "red")
        else:
            log_event(f"❌ Attack Cancelled for {label}", "red")
    threading.Thread(target=ask).start()

# Detection thread
def detection_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        log_event("❌ Could not open webcam.", "red")
        return

    last_detection = None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        results = model(frame, conf=0.5, verbose=False)
        current_label = None

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                label = class_labels.get(cls, "Unknown")
                if label not in ["Truck", "Tank"]:
                    continue

                current_label = label
                if detections[label]["start_time"] is None:
                    detections[label]["start_time"] = time.time()

                duration = time.time() - detections[label]["start_time"]
                if duration >= min_duration and not detections[label]["confirmed"]:
                    detections[label]["confirmed"] = True
                    log_event(f"✅ {label} Detected with confidence {box.conf[0].item():.2f}", "red")
                    show_popup(label)

        if current_label is None:
            detections.clear()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# GUI thread
def gui_loop():
    root = tk.Tk()
    root.title("Live Detection Logs")
    root.geometry("600x400")
    root.configure(bg="black")

    tk.Label(root, text="Surveillance Log", font=("Arial", 16), fg="white", bg="black").pack(pady=5)
    log_display = scrolledtext.ScrolledText(root, font=("Consolas", 11), bg="black", fg="white", wrap=tk.WORD)
    log_display.pack(expand=True, fill="both", padx=10, pady=10)
    log_display.configure(state="disabled")
    log_display.tag_config("red", foreground="red")

    def update_log():
        while not log_queue.empty():
            msg, tag = log_queue.get()
            log_display.configure(state="normal")
            log_display.insert(tk.END, msg + "\n")
            if tag:
                log_display.tag_add(tag, "end-2l", "end-1l")
            log_display.configure(state="disabled")
            log_display.see(tk.END)
        root.after(100, update_log)

    root.after(100, update_log)
    threading.Thread(target=detection_loop, daemon=True).start()
    root.mainloop()

# Start GUI
if __name__ == "__main__":
    gui_loop()
