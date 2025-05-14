import cv2
import torch
from ultralytics import YOLO
import logging

# Suppress YOLO logs
logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Load YOLOv11 model
model = YOLO("best.pt")  # Replace with your trained model path

# Attempt to get class names from the model

class_labels = model.names
print(class_labels)

# Open the webcam
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Perform inference
    results = model(frame, conf=0.5, verbose=False)

    # Process detections
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get bounding box coordinates
            cls = int(box.cls[0])  # Get class ID
            conf = box.conf[0].item()  # Confidence score
            label = class_labels.get(cls, "Unknown")

            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label}: {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow("Army Tanker & Truck Detection", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
