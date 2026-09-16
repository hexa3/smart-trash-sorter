import cv2
import serial
import time

from classifier import WasteClassifier

# ---- CONFIG ----
SERIAL_PORT = "/dev/ttyACM0"   # <-- change to your port
BAUD_RATE = 9600
MOTION_THRESHOLD = 25000       # tune this based on testing
COOLDOWN_SECONDS = 5           # avoid re-triggering immediately after a sort
MIN_CONFIDENCE = 0.4           # ignore guesses below this
BURST_FRAMES = 5               # frames to sample per trigger
BURST_DELAY = 0.1              # seconds between burst frames

# ---- SETUP ----
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # let the Arduino reset after serial connect

classifier = WasteClassifier()

cap = cv2.VideoCapture("http://192.168.1.114:8080/video")
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

last_trigger_time = 0


def classify_burst(classifier, cap, n=BURST_FRAMES, delay=BURST_DELAY):
    """Classify several frames and majority-vote, ignoring low-confidence guesses."""
    votes = []
    raw_seen = []
    for _ in range(n):
        ret, frame = cap.read()
        if ret:
            label, raw_label, confidence = classifier.classify(frame, min_confidence=MIN_CONFIDENCE)
            raw_seen.append(f"{raw_label} ({confidence:.0%})")
            if label != "UNKNOWN":
                votes.append(label)
        time.sleep(delay)

    if not votes:
        return "T", raw_seen  # safe default if nothing was confident
    decision = max(set(votes), key=votes.count)
    return decision, raw_seen


print("Watching for motion... (Ctrl+C to stop)")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        frame_delta = cv2.absdiff(prev_gray, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        motion_score = cv2.countNonZero(thresh)
        print(f"motion_score={motion_score}")

        now = time.time()
        if motion_score > MOTION_THRESHOLD and (now - last_trigger_time) > COOLDOWN_SECONDS:
            print(f"Motion detected (score={motion_score}) — classifying...")
            label, raw_seen = classify_burst(classifier, cap)
            print(f"  Frames seen: {raw_seen}")
            print(f"  Decision: {'Recyclable' if label=='R' else 'Trash'} — sending '{label}'")
            arduino.write(label.encode())
            last_trigger_time = now

        prev_gray = gray

finally:
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()