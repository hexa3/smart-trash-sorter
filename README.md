# Smart Trash Sorter

An automated two-bin waste sorter powered by a camera, a TensorFlow Lite image
classifier, and an Arduino-controlled mechanism. The system watches a camera
feed for motion, identifies the item placed in view, and sends a one-character
serial command to route it to the recyclable or trash bin.

> This project is a practical prototype. Treat its classifications as guidance,
> not a substitute for local recycling rules.

## How it works

```text
IP/USB camera -> motion detection -> 5-frame image classification
                                      |
                                      v
                            R (recyclable) or T (trash)
                                      |
                                      v
                           USB serial -> Arduino -> sorter
```

1. `main.py` reads frames from the camera and measures the difference from the
   previous frame.
2. When motion exceeds the configured threshold, it classifies a short burst of
   frames to reduce one-frame mistakes.
3. `classifier.py` runs MobileNetV2 through TensorFlow Lite and maps the best
   ImageNet label to recyclable (`R`) or trash (`T`).
4. The majority decision is written to the Arduino over serial at 9600 baud.

## Hardware

- A camera accessible through OpenCV (an IP Webcam stream or USB camera)
- A computer/Raspberry Pi capable of running Python and TensorFlow Lite
- Arduino connected by USB serial
- A two-way sorting mechanism driven by the Arduino

The Arduino sketch and physical mechanism are not included in this repository.
It should accept `R` and `T` characters over serial and move the corresponding
actuator.

## Setup

Requires Python 3.10+ and a connected camera/Arduino.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Before running, update the configuration at the top of `main.py`:

- `SERIAL_PORT`: your Arduino port, such as `/dev/ttyACM0` or `COM3`
- `BAUD_RATE`: must match the Arduino sketch (default `9600`)
- camera source in `cv2.VideoCapture(...)`: your camera URL or device index
- `MOTION_THRESHOLD`: tune for your lighting and camera framing

On Linux, your user may need membership in the `dialout` group to access the
serial device. Check the available ports with `ls /dev/ttyACM* /dev/ttyUSB*`.

## Project layout

```text
.
├── main.py                 # Camera loop, motion trigger, and Arduino commands
├── classifier.py           # TensorFlow Lite inference and sorting rules
├── models/
│   ├── mobilenet_v2.tflite # Runtime image-classification model
│   └── labels.txt          # ImageNet class labels
└── requirements.txt        # Python dependencies
```

## Classification behavior

The model predicts an ImageNet label, then keyword rules choose a destination.
Labels containing terms such as `bottle`, `can`, `cardboard`, or `paper` go to
`R`; labels such as `banana`, `pizza`, `napkin`, or `food` go to `T`. Predictions
below `MIN_CONFIDENCE` are ignored. If no frame in a burst is confident, the
system defaults to `T` as the safer fallback.

The keyword lists are deliberately simple and live in `classifier.py`; adjust
them for the materials your sorter is designed to handle and the recycling
guidance in your area.

## Model attribution

`models/mobilenet_v2.tflite` is the quantized MobileNetV2 ImageNet model. See
[TensorFlow's MobileNet documentation](https://www.tensorflow.org/api_docs/python/tf/keras/applications/MobileNetV2)
for architecture and model information. The project includes only the runtime
model and label file; training checkpoints and archives are intentionally not
tracked.

---

<p align="center">Built by <a href="https://sheheryar.xyz">Sheheryar</a> · <a href="https://github.com/hexa3">github.com/hexa3</a></p>
