# 🤖 AI Security Camera

An AI-powered security camera system built with **Arduino UNO Q**, a **PIR motion sensor**, a **USB camera**, and AI-based **face detection and image classification**.

The system detects motion, waits for a face to appear, captures an image, classifies the detected person as either **Family** or **Stranger**, and automatically saves and sends a cropped stranger-face snapshot through **Telegram** when an unknown person is detected.

---

## 📸 Project Overview

The **AI Security Camera** combines physical sensors, computer vision, AI image classification, and remote notifications into a single security system.

### How it works

```text
                    ┌──────────────────┐
                    │   PIR Sensor     │
                    │      D8          │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Motion Detected  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  USB Camera      │
                    │  Face Detection  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Capture Image    │
                    └────────┬─────────┘
                             │
                             ▼
                 ┌─────────────────────────┐
                 │ AI Image Classification │
                 └───────────┬─────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
             ┌────────────┐    ┌────────────┐
             │   FAMILY   │    │  STRANGER  │
             └─────┬──────┘    └─────┬──────┘
                   │                  │
                   ▼                  ▼
             No Alert           Crop Face
                                      │
                                      ▼
                               Save Snapshot
                                      │
                                      ▼
                              Telegram Alert
```

---

## ✨ Features

* 🚨 **PIR motion detection**
* 📷 **USB camera support**
* 👤 **Real-time face detection**
* 🧠 **AI Family/Stranger classification**
* 📸 **Automatic stranger face cropping**
* 💾 **Local stranger snapshot storage**
* 📱 **Telegram security alerts**
* ⏱️ **Classification cooldown**
* 🔒 **One classification result per motion event**
* 🎯 **Configurable confidence thresholds**
* 🕒 **New York local timestamp support**
* 💡 **LED motion indicator**
* 🔌 **Arduino UNO Q RouterBridge communication**
* 🧵 **Background classification using Python threading**

---

# 🧰 Hardware

## Required Hardware

| Component         | Description                        | Connection    |
| ----------------- | ---------------------------------- | ------------- |
| Arduino UNO Q     | Main controller                    | —             |
| PIR Motion Sensor | Detects movement                   | D8            |
| LED               | Motion status indicator            | D3            |
| USB Webcam        | Captures images                    | USB           |
| USB Hub           | Optional, depending on peripherals | USB           |
| Display           | Display the dashboard              | USB Hub(HTMI) |

### Hardware connections

```text
PIR Sensor
───────────
VCC  → 5V
GND  → GND
OUT  → D8


LED
───
Anode (+) → D3 through resistor
Cathode (-) → GND


USB Camera
──────────
USB → Arduino UNO Q USB port
       or USB hub
```

> ⚠️ Always verify the voltage requirements and pinout of your specific PIR sensor and LED before connecting hardware.

---

# 💻 Software

This project uses the Arduino UNO Q's Linux/Python environment together with the Arduino microcontroller environment.

### Main technologies

* Arduino App Lab
* Arduino RouterBridge
* AI Image Classification
* AI Video Object Detection
* Telegram Bot API

---

# 📁 Project Structure

A recommended GitHub structure is:

```text
AI-Security-Camera/
│
├── sketch/
│   └── sketch.ino
│
├── python/
│   └── main.py
│
├── .gitignore
├── README.md
└── LICENSE
```

Depending on how your Arduino App Lab project is exported, your actual filenames may differ.

---

# ⚙️ Configuration

The Python application contains several configuration parameters.

```python
PIR_PIN = 8

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

FACE_CONFIDENCE = 0.60

CLASSIFICATION_THRESHOLD = 0.80

CLASSIFICATION_COOLDOWN = 5.0

ONE_RESULT_PER_MOTION = True

FACE_PADDING_X = 0.40
FACE_PADDING_Y = 0.40

SNAPSHOT_FOLDER = "stranger_snapshots"

TIMEZONE = ZoneInfo("America/New_York")
```

## Camera Resolution

```python
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
```

The current configuration uses:

**640 × 480 pixels**

This provides a good balance between image quality and processing performance.

---

## Face Detection Confidence

```python
FACE_CONFIDENCE = 0.60
```

The face detector requires at least **60% confidence** before treating an object as a detected face.

Increase this value if the system produces false detections.

For example:

```python
FACE_CONFIDENCE = 0.70
```

---

## Classification Threshold

```python
CLASSIFICATION_THRESHOLD = 0.80
```

A classification must reach at least **80% confidence** before the system makes a Family or Stranger decision.

### Family

The system identifies a person as Family when:

```text
Family confidence ≥ 80%
AND
Family confidence > Stranger confidence
```

### Stranger

The system identifies a person as Stranger when:

```text
Stranger confidence ≥ 80%
AND
Stranger confidence > Family confidence
```

Otherwise, the result is:

```text
UNCERTAIN
```

No alert or snapshot is generated for an uncertain result.

---

# 📱 Telegram Setup

The system can send a Telegram alert whenever a stranger is detected.

The code contains:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
```

Replace these values with your own Telegram Bot credentials.

### ⚠️ Security

**Never commit your real bot token to GitHub.**

Instead of:

```python
BOT_TOKEN = "123456789:ABC..."
```

use a secure configuration method such as environment variables.

For example:

```python
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
```

Then configure the variables in your local environment.

---

# 🚨 Stranger Detection Workflow

When the PIR sensor detects motion:

```text
PIR detects motion
        ↓
Face detection activated
        ↓
Face detected
        ↓
Camera captures frame
        ↓
AI classification
        ↓
 ┌───────────────┐
 │ Family?       │
 └───────┬───────┘
         │
    Yes  │  No
         │
         ▼
   ┌───────────┐
   │ Stranger? │
   └─────┬─────┘
         │
        Yes
         │
         ▼
  Crop detected face
         │
         ▼
 Save JPEG snapshot
         │
         ▼
 Send Telegram alert
```

---

# 👤 Family Detection

When the AI determines that the detected person is a family member:

```text
🟢 FAMILY MEMBER
```

The system:

* Does not save a stranger snapshot
* Does not send a Telegram alert
* Returns to monitoring

Example:

```text
Family confidence: 94.32%
Stranger confidence: 5.68%

🟢 FAMILY MEMBER

No snapshot saved.
No Telegram alert.
```

---

# 🚨 Stranger Detection

When the AI determines that the person is a stranger:

```text
🚨 STRANGER DETECTED
```

The system:

1. Retrieves the detected face bounding box.
2. Adds configurable padding around the face.
3. Crops the face.
4. Saves the image as a JPEG.
5. Sends the image to Telegram.
6. Includes confidence and timestamp information.

Example filename:

```text
stranger_face_20260911_185932_94pct.jpg
```

The filename contains:

```text
stranger_face
    ↓
YYYYMMDD
    ↓
HHMMSS
    ↓
confidence percentage
```

---

# 📸 Face Snapshot

The system uses the face bounding box supplied by the video detection system.

Example:

```python
face_box = (
    x1,
    y1,
    x2,
    y2
)
```

Padding is added around the detected face:

```python
FACE_PADDING_X = 0.40
FACE_PADDING_Y = 0.40
```

This prevents the saved image from being an excessively tight crop.

The crop coordinates are also clamped to the camera image boundaries to prevent invalid image regions.

---

# 📱 Telegram Alert

A stranger alert contains information similar to:

```text
🚨 SECURITY CAMERA ALERT

🚨 STRANGER DETECTED

Confidence: 94.25%
Time: September 11, 2026 at 06:59:32 PM EDT

📸 Stranger face snapshot attached.
```

The cropped face image is attached to the Telegram message.

---

# 💡 LED Status

The Arduino sketch controls an LED connected to **D3**.

### Motion detected

```text
PIR = HIGH
     ↓
LED = ON
```

### Motion ended

```text
PIR = LOW
     ↓
LED = OFF
```

The Arduino code also includes a small debounce interval:

```cpp
unsigned long debounce_delay = 50;
```

This helps prevent rapid state changes caused by sensor noise.

---

# 🔌 Arduino RouterBridge

The Arduino microcontroller provides the PIR state to Python through RouterBridge.

The function:

```cpp
int get_pir_state()
{
    return digitalRead(PIR_PIN);
}
```

is registered with:

```cpp
Bridge.provide("get_pir_state", get_pir_state);
```

The Python application then reads the PIR state using:

```python
state = Bridge.call("get_pir_state")
```

This creates the communication path:

```text
PIR Sensor
    ↓
Arduino D8
    ↓
Arduino_RouterBridge
    ↓
Python
    ↓
AI Security Application
```

---

# 🧠 AI Processing

The project uses two separate computer-vision stages.

## Stage 1 — Face Detection

The video object detection system searches the camera stream for faces.

```python
detection_stream = VideoObjectDetection(
    camera=camera,
    confidence=FACE_CONFIDENCE,
    debounce_sec=1.0
)
```

When a face is detected:

```python
detection_stream.on_detect(
    "face",
    face_detected
)
```

The face callback starts the classification process.

---

## Stage 2 — Family/Stranger Classification

The captured camera image is passed to the image classification model:

```python
results = image_classification.classify(
    image,
    image_type="jpeg",
    confidence=0.0
)
```

The application then reads:

```text
family
stranger
```

classification results and compares their confidence values.

---

# ⏱️ Classification Cooldown

To prevent excessive AI processing, the project uses:

```python
CLASSIFICATION_COOLDOWN = 5.0
```

This means the system waits at least **5 seconds** between classifications.

This helps reduce:

* CPU usage
* repeated processing
* duplicate alerts
* unnecessary camera captures

---

# 1️⃣ One Result Per Motion Event

The project also supports:

```python
ONE_RESULT_PER_MOTION = True
```

When enabled, the system performs only one classification for each PIR motion event.

For example:

```text
Motion starts
    ↓
Face detected
    ↓
Classification
    ↓
Stranger
    ↓
Telegram alert
    ↓
Additional face detections ignored
    ↓
Motion ends
    ↓
System resets
```

When the next motion event begins, the classification state is reset.

---

# 🕒 Time Zone

The application uses:

```python
TIMEZONE = ZoneInfo("America/New_York")
```

Local timestamps are generated using:

```python
datetime.now(TIMEZONE)
```

This ensures Telegram alerts and saved snapshot timestamps use New York time.

---

# ▶️ Running the Project

## 1. Connect the Hardware

Connect:

```text
PIR OUT → D8
LED     → D3
USB Camera → UNO Q USB
```

---

## 2. Upload the Arduino Sketch

Open the Arduino sketch in Arduino App Lab and upload/run the microcontroller portion.

The Arduino application should display:

```text
================================
AI SECURITY CAMERA
PIR + LED CONTROL READY
================================
PIR Pin: D8
LED Pin: D3
================================
```

---

## 3. Configure Telegram

Set:

```python
BOT_TOKEN
CHAT_ID
```

using a secure configuration method.

---

## 4. Start the Python Application

The application initializes:

```text
Image Classification
        ↓
Camera
        ↓
Face Detection
        ↓
PIR Monitoring
        ↓
Main Application Loop
```

A successful startup should display messages similar to:

```text
==================================================
AI SECURITY CAMERA
CHECKPOINT D-6C
PIR + FACE + FAMILY / STRANGER
+ STRANGER FACE SNAPSHOT
+ TELEGRAM ALERT
==================================================

System is starting...

Initializing Image Classification...
✅ Image Classification initialized!

Initializing Camera...
✅ Camera initialized!

Initializing Face Detection...
✅ Face Detection initialized!
```

---

# 🧪 Testing

## Test 1 — PIR Sensor

Move in front of the PIR sensor.

Expected result:

```text
🚨 PIR MOTION DETECTED
```

The LED connected to D3 should turn on.

---

## Test 2 — Face Detection

After motion is detected, place a face in front of the camera.

Expected result:

```text
👤 FACE DETECTED
```

---

## Test 3 — Family Classification

Present a person that the model recognizes as Family.

Expected result:

```text
🟢 FAMILY MEMBER

No snapshot saved.
No Telegram alert.
```

---

## Test 4 — Stranger Classification

Present a person that the model recognizes as Stranger.

Expected result:

```text
🚨 STRANGER DETECTED
```

Then:

```text
📸 STRANGER FACE SNAPSHOT SAVED
```

followed by:

```text
✅ Telegram stranger alert sent successfully.
```

---

## Test 5 — Uncertain Classification

If neither Family nor Stranger reaches the configured threshold:

```text
⚠️ UNCERTAIN
```

The system should not send a Telegram alert.

---

# 🛠️ Troubleshooting

## Camera does not initialize

Check:

* USB camera connection
* USB hub connection
* Camera compatibility
* Arduino UNO Q USB connection
* Camera permissions
* Arduino App Lab camera configuration

---

## PIR does not detect motion

Check:

```text
PIR OUT → D8
PIR VCC → appropriate power
PIR GND → GND
```

Also allow the PIR sensor time to initialize after power-up.

---

## LED does not turn on

Verify:

```text
D3 → resistor → LED anode
LED cathode → GND
```

Also check that the LED is not connected backward.

---

## No face is detected

Try:

* Improving lighting
* Moving closer to the camera
* Positioning the face directly toward the camera
* Lowering `FACE_CONFIDENCE`
* Checking the camera resolution

For example:

```python
FACE_CONFIDENCE = 0.50
```

---

## Classification returns UNCERTAIN

Try:

* Improving lighting
* Retraining/improving the Family/Stranger model
* Increasing image quality
* Positioning the person closer to the camera
* Reviewing the classification confidence
* Adjusting `CLASSIFICATION_THRESHOLD`

---

## Telegram alert fails

Check:

```text
BOT_TOKEN
CHAT_ID
Internet connection
Telegram bot configuration
```

The application prints the HTTP status and Telegram response when an API error occurs.

---

## Snapshot is not saved

Check:

```text
stranger_snapshots/
```

The application automatically creates the directory:

```python
os.makedirs(
    SNAPSHOT_FOLDER,
    exist_ok=True
)
```

Also verify that a valid face bounding box was received.

---

# 🔐 Privacy & Security

This project processes camera images and potentially identifies people, so privacy should be considered carefully.

### Recommendations

* Do not publish real face images in the repository.
* Do not commit Telegram bot credentials.
* Add `stranger_snapshots/` to `.gitignore`.
* Only use the system where you have appropriate permission.
* Inform people when camera monitoring is required by local rules.
* Avoid storing images longer than necessary.
* Protect the device and network connection.

---

# 🚫 .gitignore

Create a `.gitignore` file containing:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
env/

# Environment variables
.env
.env.*

# Security camera snapshots
stranger_snapshots/*
!stranger_snapshots/.gitkeep

# Logs
*.log

# IDE
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db
```

This helps prevent accidentally uploading captured faces and private configuration data.

---

# 📊 System Parameters

| Parameter                |    Current Value | Purpose                          |
| ------------------------ | ---------------: | -------------------------------- |
| PIR Pin                  |               D8 | Motion detection                 |
| LED Pin                  |               D3 | Motion indicator                 |
| Camera Width             |              640 | Image width                      |
| Camera Height            |              480 | Image height                     |
| Face Confidence          |             0.60 | Face detection threshold         |
| Classification Threshold |             0.80 | Family/Stranger threshold        |
| Classification Cooldown  |            5 sec | Prevent repeated processing      |
| One Result Per Motion    |          Enabled | Prevent duplicate classification |
| Face X Padding           |              40% | Horizontal crop padding          |
| Face Y Padding           |              40% | Vertical crop padding            |
| Time Zone                | America/New_York | Alert timestamps                 |

---

# 🧩 System Architecture

```text
┌───────────────────────────────────────────────┐
│               ARDUINO UNO Q                   │
│                                               │
│   ┌─────────────┐       ┌──────────────┐     │
│   │ PIR Sensor  │──────▶│ Arduino D8   │     │
│   └─────────────┘       └──────┬───────┘     │
│                                │              │
│                         RouterBridge           │
│                                │              │
│   ┌─────────────┐              │              │
│   │ LED / D3    │◀─────────────┘              │
│   └─────────────┘                             │
│                                               │
│             USB Camera                        │
│                 │                             │
│                 ▼                             │
│        ┌──────────────────┐                   │
│        │ Python AI Layer  │                   │
│        └────────┬─────────┘                   │
│                 │                             │
│        ┌────────▼─────────┐                   │
│        │ Face Detection   │                   │
│        └────────┬─────────┘                   │
│                 │                             │
│        ┌────────▼─────────┐                   │
│        │ Image Capture    │                   │
│        └────────┬─────────┘                   │
│                 │                             │
│        ┌────────▼─────────┐                   │
│        │ Family/Stranger  │                   │
│        │ Classification   │                   │
│        └────────┬─────────┘                   │
│                 │                             │
│        ┌────────┴─────────┐                   │
│        ▼                  ▼                   │
│     FAMILY            STRANGER                │
│                           │                   │
│                           ▼                   │
│                    Face Snapshot              │
│                           │                   │
│                           ▼                   │
│                     Telegram API              │
└───────────────────────────┼───────────────────┘
                            │
                            ▼
                       📱 Telegram
```

---

# 🚀 Future Improvements

Possible future versions of the project could include:

* 🎙️ AI voice commands
* 🏠 Integration with **HomeMind**
* 🌡️ Home environmental monitoring
* 🌐 Web-based security dashboard
* 📊 Security event history
* 🖼️ Browser-based snapshot gallery
* 🔔 Multiple notification channels
* 👨‍👩‍👧 Multiple known-family profiles
* 🧠 Improved person recognition
* 🚪 Door/window sensor integration
* 🔐 Arm/disarm security modes
* 🌙 Night mode
* 💡 Automatic security lighting
* ☁️ Optional secure remote backup
* 📈 Detection statistics
* 📱 Mobile-friendly monitoring interface

---

# 🏠 HomeMind Integration

This AI Security Camera can serve as the security component of a larger **HomeMind** smart-home system.

A future integrated architecture could look like:

```text
                    HOME MIND
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   Security        Climate       Air Quality
    Camera         Monitor          Monitor
        │              │              │
        ▼              ▼              ▼
      PIR            DHT11           AQI
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
                 AI Home System
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        Web Dashboard        Telegram
```

The security camera can therefore become one module within a broader intelligent home automation platform.

---

# 📌 Project Status

### Current checkpoint: D-6C

Implemented:

* [x] PIR motion detection
* [x] Arduino RouterBridge communication
* [x] USB camera initialization
* [x] Face detection
* [x] Face bounding-box extraction
* [x] Camera image capture
* [x] Family/Stranger classification
* [x] Classification confidence threshold
* [x] One result per PIR event
* [x] Classification cooldown
* [x] Stranger face cropping
* [x] Local JPEG snapshot
* [x] New York timestamps
* [x] Telegram photo alert
* [x] Telegram error handling
* [x] Camera shutdown handling

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

If you would like to contribute:

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/my-new-feature
```

3. Commit your changes.

```bash
git commit -m "Add new security feature"
```

4. Push the branch.

```bash
git push origin feature/my-new-feature
```

5. Open a Pull Request.

---

# 📄 License

This project is available under the **MIT License** unless otherwise specified.

See `LICENSE` for details.

---

# ⭐ Acknowledgments

This project was developed using the Arduino UNO Q platform and Arduino App Lab ecosystem, combining embedded hardware with Python-based AI and computer vision.

Special thanks to the open-source and developer communities behind the tools and libraries used in this project.

---

## 👨‍💻 Author

**William Liu**

AI / ML • Computer Vision • Embedded Systems • Robotics • Engineering

---

## ⭐ If you find this project useful

Consider giving the repository a ⭐ on GitHub!

```text
AI Security Camera
Arduino UNO Q + PIR + Computer Vision + AI
                         │
                         ▼
                Family / Stranger
                         │
                         ▼
              Snapshot + Telegram
```
