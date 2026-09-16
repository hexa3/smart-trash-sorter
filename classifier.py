"""
classifier.py — local offline waste classifier using MobileNetV2 (TFLite)
"""

import numpy as np
from PIL import Image

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    from ai_edge_litert.interpreter import Interpreter as _Interpreter
    class tflite:
        Interpreter = _Interpreter

MODEL_PATH = "models/mobilenet_v2.tflite"
LABELS_PATH = "models/labels.txt"

RECYCLABLE_KEYWORDS = [
    "bottle", "can", "tin", "cardboard", "carton", "newspaper",
    "envelope", "paper", "jar", "container", "packet", "wrapper",
    "box", "crate", "milk_can", "pop_bottle", "beer_bottle",
    "wine_bottle", "water_bottle", "soda",
]

TRASH_KEYWORDS = [
    "banana", "orange", "lemon", "apple", "pizza", "ice_cream",
    "cup", "paper_towel", "diaper", "cigarette", "napkin",
    "food", "fruit", "vegetable", "meat", "bone",
]


class WasteClassifier:
    def __init__(self, model_path=MODEL_PATH, labels_path=LABELS_PATH):
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.input_shape = self.input_details[0]['shape'][1:3]
        with open(labels_path, "r") as f:
            self.labels = [line.strip() for line in f.readlines()]

    def _preprocess(self, frame_bgr):
        img = Image.fromarray(frame_bgr[:, :, ::-1])
        img = img.resize((self.input_shape[1], self.input_shape[0]))
        arr = np.array(img, dtype=np.uint8)
        arr = np.expand_dims(arr, axis=0)
        return arr

    def predict_label(self, frame_bgr):
        input_data = self._preprocess(frame_bgr)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        top_idx = int(np.argmax(output))
        confidence = float(output[top_idx]) / 255.0
        label = self.labels[top_idx] if top_idx < len(self.labels) else "unknown"
        return label, confidence

    def classify(self, frame_bgr, min_confidence=0.4):
        label, confidence = self.predict_label(frame_bgr)
        label_lower = label.lower()

        if confidence < min_confidence:
            return "UNKNOWN", label, confidence

        if any(kw in label_lower for kw in RECYCLABLE_KEYWORDS):
            decision = "R"
        elif any(kw in label_lower for kw in TRASH_KEYWORDS):
            decision = "T"
        else:
            decision = "T"

        return decision, label, confidence
