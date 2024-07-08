import cv2
import numpy as np

# Function to detect the color of the ball
def detect_color(frame, lower_bound, upper_bound):
    mask = cv2.inRange(frame, lower_bound, upper_bound)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours

# Define quadrants
def define_quadrants(frame):
    height, width, _ = frame.shape
    return {
        1: (0, height // 2, 0, width // 2),
        2: (0, height // 2, width // 2, width),
        3: (height // 2, height, 0, width // 2),
        4: (height // 2, height, width // 2, width)
    }

# Check if the ball is within a quadrant
def is_within_quadrant(cx, cy, quadrant):
    y1, y2, x1, x2 = quadrant
    return x1 <= cx <= x2 and y1 <= cy <= y2

# Load the video
video_path = r"C:\Users\Anjii\OneDrive\Documents\AI Role\AI Assignment video.mp4"  
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps
print(f"Video loaded: {frame_count} frames at {fps} fps, duration: {duration:.2f} seconds.")

# Define color bounds for yellow, white, green, and red balls in HSV space
color_bounds = {
    "yellow": ([20, 100, 100], [30, 255, 255]),
    "white": ([0, 0, 200], [180, 30, 255]),
    "green": ([36, 25, 25], [86, 255, 255]),
    "red": ([0, 120, 70], [10, 255, 255])
}

# Convert the bounds to numpy arrays
for color in color_bounds:
    color_bounds[color] = (np.array(color_bounds[color][0], dtype="uint8"),
                           np.array(color_bounds[color][1], dtype="uint8"))

# Define quadrants
quadrants = None
events = []

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('processed_video.avi', fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

# Process video frames
frame_number = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_number += 1
    if quadrants is None:
        quadrants = define_quadrants(frame)
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for color, (lower, upper) in color_bounds.items():
        contours = detect_color(hsv, lower, upper)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cx, cy = x + w // 2, y + h // 2
            
            for quadrant_number, bounds in quadrants.items():
                if is_within_quadrant(cx, cy, bounds):
                    # Determine the type of event (entry or exit)
                    # Here we assume entry for simplicity, but this should be determined based on previous state
                    event_type = "Entry"
                    timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    events.append((timestamp, quadrant_number, color, event_type))
                    
                    # Overlay text on frame
                    text = f"{event_type} at {timestamp:.2f}s"
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    # Write the frame with the overlay to the output video
    out.write(frame)
    print(f"Processed frame {frame_number}/{frame_count}")

cap.release()
out.release()

# Write events to text file
with open("events.txt", "w") as file:
    for event in events:
        file.write(f"{event[0]}, {event[1]}, {event[2]}, {event[3]}\n")

print("Processing complete. Processed video saved as 'processed_video.avi' and events logged in 'events.txt'.")
