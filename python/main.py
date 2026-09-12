# ============================================================
# AI SECURITY CAMERA
# CHECKPOINT D-6C
#
# PIR -> FACE DETECTION -> CLASSIFICATION
# -> STRANGER FACE SNAPSHOT -> TELEGRAM ALERT
#
# Arduino UNO Q
# PIR: D8
# Camera: USB Webcam
#
# No WebUI dependency
# No Telegram polling
# ============================================================

import os
import time
import threading
import requests
import numpy as np

from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo

from arduino.app_utils import App, Bridge
from arduino.app_peripherals.camera import Camera
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_bricks.image_classification import ImageClassification


# ============================================================
# CONFIGURATION
# ============================================================

PIR_PIN = 8

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

FACE_CONFIDENCE = 0.60

CLASSIFICATION_THRESHOLD = 0.80

# Minimum time between classifications.
CLASSIFICATION_COOLDOWN = 5.0

# Prevent repeated processing during the same PIR event.
ONE_RESULT_PER_MOTION = True

# Padding around detected face.
FACE_PADDING_X = 0.40
FACE_PADDING_Y = 0.40

# Where stranger face snapshots are saved.
SNAPSHOT_FOLDER = "stranger_snapshots"

# New York timezone.
TIMEZONE = ZoneInfo("America/New_York")


# ============================================================
# TELEGRAM CONFIGURATION
# ============================================================

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# ============================================================
# CREATE SNAPSHOT DIRECTORY
# ============================================================

os.makedirs(
    SNAPSHOT_FOLDER,
    exist_ok=True
)


# ============================================================
# GLOBAL STATE
# ============================================================

pir_active = False

# Prevent multiple face callbacks from triggering
# multiple classifications during the same PIR event.
classification_completed_for_motion = False

classification_running = False

last_classification_time = 0.0

classification_lock = threading.Lock()

# Latest face bounding box supplied by VideoObjectDetection.
latest_face_box = None

latest_face_confidence = 0.0

face_data_lock = threading.Lock()


# ============================================================
# TIME FUNCTIONS
# ============================================================

def get_local_time():
    return datetime.now(TIMEZONE)


def formatted_local_time():
    return get_local_time().strftime(
        "%B %d, %Y at %I:%M:%S %p %Z"
    )


# ============================================================
# STARTUP
# ============================================================

print()
print("=" * 50)
print("AI SECURITY CAMERA")
print("CHECKPOINT D-6C")
print("PIR + FACE + FAMILY / STRANGER")
print("+ STRANGER FACE SNAPSHOT")
print("+ TELEGRAM ALERT")
print("=" * 50)

print()
print("System is starting...")


# ============================================================
# TELEGRAM CONFIGURATION CHECK
# ============================================================

if (
    BOT_TOKEN == "YOUR_BOT_TOKEN"
    or CHAT_ID == "YOUR_CHAT_ID"
):

    print()
    print("⚠️ Telegram is NOT configured.")
    print("Set BOT_TOKEN and CHAT_ID before testing")
    print("Telegram alerts.")

else:

    print()
    print("✅ Telegram configuration detected.")


# ============================================================
# INITIALIZE IMAGE CLASSIFICATION
# ============================================================

print()
print("Initializing Image Classification...")

try:

    image_classification = ImageClassification()

    print("✅ Image Classification initialized!")

except Exception as e:

    print("❌ Image Classification initialization failed:")
    print(repr(e))

    raise


# ============================================================
# INITIALIZE CAMERA
# ============================================================

print()
print("Initializing Camera...")

try:

    camera = Camera(
        resolution=(
            CAMERA_WIDTH,
            CAMERA_HEIGHT
        )
    )

    camera.start()

    print("✅ Camera initialized!")

except Exception as e:

    print("❌ Camera initialization failed:")
    print(repr(e))

    raise


# ============================================================
# INITIALIZE FACE DETECTION
# ============================================================

print()
print("Initializing Face Detection...")

try:

    detection_stream = VideoObjectDetection(
        camera=camera,
        confidence=FACE_CONFIDENCE,
        debounce_sec=1.0
    )

    print("✅ Face Detection initialized!")

except Exception as e:

    print("❌ Face Detection initialization failed:")
    print(repr(e))

    raise


# ============================================================
# STORE FACE DETECTION DATA
#
# IMPORTANT:
#
# on_detect("face", callback) does not provide the
# bounding box.
#
# on_detect_all() provides:
#
# {
#     'face': [
#         {
#             'confidence': ...,
#             'bounding_box_xyxy': (...)
#         }
#     ]
# }
# ============================================================

def receive_detection_data(detections):

    global latest_face_box
    global latest_face_confidence

    try:

        if not isinstance(detections, dict):
            return

        faces = detections.get("face", [])

        if not faces:
            return

        # Use the first detected face.
        face = faces[0]

        if not isinstance(face, dict):
            return

        box = face.get(
            "bounding_box_xyxy"
        )

        confidence = face.get(
            "confidence",
            0.0
        )

        if box is None:
            return

        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.0

        with face_data_lock:

            latest_face_box = tuple(
                int(v) for v in box
            )

            latest_face_confidence = confidence

    except Exception as e:

        print(
            "⚠️ Detection data error:",
            repr(e)
        )


# ============================================================
# FACE DETECTED CALLBACK
# ============================================================

def face_detected():

    global classification_completed_for_motion
    global classification_running

    # --------------------------------------------------------
    # FACE DETECTED BEFORE PIR?
    # --------------------------------------------------------

    if not pir_active:

        return

    # --------------------------------------------------------
    # ONLY ONE RESULT PER PIR MOTION EVENT
    # --------------------------------------------------------

    if ONE_RESULT_PER_MOTION:

        if classification_completed_for_motion:

            return

        # Lock the event immediately.
        #
        # This prevents multiple face detections from
        # starting multiple classification threads.
        classification_completed_for_motion = True

    print()
    print("=" * 50)
    print("👤 FACE DETECTED")
    print("=" * 50)

    print(
        "Time:",
        formatted_local_time()
    )

    print(
        "Face detected after PIR motion."
    )

    print(
        "➡️ Capturing image for classification..."
    )

    # --------------------------------------------------------
    # START CLASSIFICATION THREAD
    # --------------------------------------------------------

    thread = threading.Thread(
        target=classify_and_process,
        daemon=True
    )

    thread.start()


# ============================================================
# REGISTER VIDEO DETECTION CALLBACKS
# ============================================================

detection_stream.on_detect(
    "face",
    face_detected
)

detection_stream.on_detect_all(
    receive_detection_data
)


# ============================================================
# CLASSIFY CURRENT CAMERA IMAGE
# ============================================================

def classify_and_process():

    global classification_running
    global last_classification_time

    # --------------------------------------------------------
    # PREVENT CONCURRENT CLASSIFICATION
    # --------------------------------------------------------

    with classification_lock:

        if classification_running:

            print(
                "⏳ Classification already running."
            )

            return

        classification_running = True

    try:

        # ----------------------------------------------------
        # COOLDOWN
        # ----------------------------------------------------

        current_time = time.time()

        elapsed = (
            current_time
            - last_classification_time
        )

        if elapsed < CLASSIFICATION_COOLDOWN:

            remaining = (
                CLASSIFICATION_COOLDOWN
                - elapsed
            )

            print(
                f"⏳ Classification cooldown: "
                f"{remaining:.1f}s"
            )

            return

        last_classification_time = current_time

        # ----------------------------------------------------
        # CAPTURE CAMERA IMAGE
        # ----------------------------------------------------

        print()
        print("----------------------------------------")
        print("📷 CAPTURING CAMERA IMAGE")
        print("----------------------------------------")

        frame = camera.capture()

        if frame is None:

            print(
                "❌ Camera returned no image."
            )

            return

        print(
            "✅ Image captured."
        )

        # ----------------------------------------------------
        # CONVERT TO PIL
        # ----------------------------------------------------

        image = Image.fromarray(frame)

        print(
            f"Image size: "
            f"{image.width} x {image.height}"
        )

        # ----------------------------------------------------
        # GET LATEST FACE BOUNDING BOX
        # ----------------------------------------------------

        with face_data_lock:

            face_box = latest_face_box
            face_confidence = latest_face_confidence

        if face_box is not None:

            print(
                "Using face box:",
                face_box
            )

            print(
                f"Face detection confidence: "
                f"{face_confidence * 100:.2f}%"
            )

        else:

            print(
                "⚠️ No face bounding box currently available."
            )

        # ----------------------------------------------------
        # CLASSIFICATION
        # ----------------------------------------------------

        print()
        print(
            "🧠 Running Family/Stranger classification..."
        )

        results = image_classification.classify(
            image,
            image_type="jpeg",
            confidence=0.0
        )

        if results is None:

            print(
                "❌ Classification returned no results."
            )

            return

        print(
            "✅ Classification completed."
        )

        # ----------------------------------------------------
        # READ RESULTS
        # ----------------------------------------------------

        classifications = results.get(
            "classification",
            []
        )

        if not classifications:

            print(
                "⚠️ No classification entries."
            )

            return

        family_confidence = 0.0
        stranger_confidence = 0.0

        print()
        print("=" * 40)
        print("CLASSIFICATION RESULTS")
        print("=" * 40)

        for item in classifications:

            class_name = str(
                item.get(
                    "class_name",
                    "unknown"
                )
            ).lower()

            raw_confidence = item.get(
                "confidence",
                0
            )

            try:

                confidence = float(
                    raw_confidence
                )

            except Exception:

                confidence = 0.0

            # Handle either:
            #
            # 0.98
            #
            # or:
            #
            # 98.0
            #

            if confidence > 1.0:

                confidence_decimal = (
                    confidence / 100.0
                )

                confidence_percent = confidence

            else:

                confidence_decimal = confidence

                confidence_percent = (
                    confidence * 100.0
                )

            print(
                f"{class_name}: "
                f"{confidence_percent:.2f}%"
            )

            if class_name == "family":

                family_confidence = (
                    confidence_decimal
                )

            elif class_name == "stranger":

                stranger_confidence = (
                    confidence_decimal
                )

        # ----------------------------------------------------
        # FINAL DECISION
        # ----------------------------------------------------

        print()
        print("=" * 40)
        print("FINAL DECISION")
        print("=" * 40)

        print(
            f"Family confidence: "
            f"{family_confidence * 100:.2f}%"
        )

        print(
            f"Stranger confidence: "
            f"{stranger_confidence * 100:.2f}%"
        )

        # ====================================================
        # FAMILY
        # ====================================================

        if (
            family_confidence
            >= CLASSIFICATION_THRESHOLD
            and
            family_confidence
            > stranger_confidence
        ):

            print()
            print("🟢 FAMILY MEMBER")
            print(
                f"Family confidence: "
                f"{family_confidence * 100:.2f}%"
            )

            print(
                "No snapshot saved."
            )

            print(
                "No Telegram alert."
            )

        # ====================================================
        # STRANGER
        # ====================================================

        elif (
            stranger_confidence
            >= CLASSIFICATION_THRESHOLD
            and
            stranger_confidence
            > family_confidence
        ):

            print()
            print("🚨 STRANGER DETECTED")

            print(
                f"Stranger confidence: "
                f"{stranger_confidence * 100:.2f}%"
            )

            # ------------------------------------------------
            # SAVE FACE SNAPSHOT
            # ------------------------------------------------

            snapshot_file = save_stranger_face_snapshot(
                image=image,
                face_box=face_box,
                stranger_confidence=stranger_confidence
            )

            if snapshot_file is not None:

                print()
                print(
                    "📸 Stranger face snapshot completed."
                )

                # --------------------------------------------
                # SEND TELEGRAM ALERT
                # --------------------------------------------

                telegram_success = (
                    send_stranger_telegram_alert(
                        snapshot_file,
                        stranger_confidence
                    )
                )

                print()

                if telegram_success:

                    print("=" * 40)
                    print("✅ CHECKPOINT D-6C SUCCESS")
                    print("=" * 40)
                    print(
                        "Stranger detected."
                    )
                    print(
                        "Face snapshot saved."
                    )
                    print(
                        "Telegram alert sent."
                    )
                    print("=" * 40)

                else:

                    print("=" * 40)
                    print(
                        "⚠️ STRANGER DETECTED"
                    )
                    print(
                        "Face snapshot saved."
                    )
                    print(
                        "Telegram alert failed."
                    )
                    print("=" * 40)

            else:

                print(
                    "❌ Stranger face snapshot failed."
                )

                print(
                    "⚠️ Telegram alert NOT sent."
                )

        # ====================================================
        # UNCERTAIN
        # ====================================================

        else:

            print()
            print("⚠️ UNCERTAIN")

            print(
                "No snapshot saved."
            )

            print(
                "No Telegram alert."
            )

        print("=" * 40)

    except Exception as e:

        print()
        print("=" * 40)
        print("❌ CLASSIFICATION ERROR")
        print("=" * 40)

        print(
            repr(e)
        )

    finally:

        classification_running = False


# ============================================================
# SAVE STRANGER FACE SNAPSHOT
# ============================================================

def save_stranger_face_snapshot(
    image,
    face_box,
    stranger_confidence
):

    print()
    print("----------------------------------------")
    print("📸 PREPARING STRANGER FACE SNAPSHOT")
    print("----------------------------------------")

    if face_box is None:

        print(
            "❌ No face bounding box available."
        )

        print(
            "❌ Stranger snapshot was NOT saved."
        )

        return None

    try:

        image_width = image.width
        image_height = image.height

        # ----------------------------------------------------
        # ORIGINAL BOUNDING BOX
        # ----------------------------------------------------

        x1, y1, x2, y2 = face_box

        print()
        print(
            "📐 FACE BOUNDING BOX"
        )

        print(
            "Original box:",
            face_box
        )

        print(
            f"Face size: "
            f"{x2 - x1} x {y2 - y1}"
        )

        print(
            f"Camera size: "
            f"{image_width} x {image_height}"
        )

        # ----------------------------------------------------
        # FACE DIMENSIONS
        # ----------------------------------------------------

        face_width = x2 - x1
        face_height = y2 - y1

        # ----------------------------------------------------
        # ADD PADDING
        #
        # This gives the snapshot some space around the face
        # while still keeping it face-focused.
        # ----------------------------------------------------

        padding_x = int(
            face_width
            * FACE_PADDING_X
        )

        padding_y = int(
            face_height
            * FACE_PADDING_Y
        )

        crop_x1 = max(
            0,
            x1 - padding_x
        )

        crop_y1 = max(
            0,
            y1 - padding_y
        )

        crop_x2 = min(
            image_width,
            x2 + padding_x
        )

        crop_y2 = min(
            image_height,
            y2 + padding_y
        )

        crop_box = (
            crop_x1,
            crop_y1,
            crop_x2,
            crop_y2
        )

        print(
            "Crop box:",
            crop_box
        )

        # ----------------------------------------------------
        # CROP FACE
        # ----------------------------------------------------

        face_image = image.crop(
            crop_box
        )

        # ----------------------------------------------------
        # FILENAME
        # ----------------------------------------------------

        local_time = get_local_time()

        timestamp = local_time.strftime(
            "%Y%m%d_%H%M%S"
        )

        confidence_percent = int(
            stranger_confidence * 100
        )

        filename = (
            f"stranger_face_"
            f"{timestamp}_"
            f"{confidence_percent}pct.jpg"
        )

        filepath = os.path.join(
            SNAPSHOT_FOLDER,
            filename
        )

        # ----------------------------------------------------
        # SAVE JPEG
        # ----------------------------------------------------

        face_image.save(
            filepath,
            format="JPEG",
            quality=95
        )

        print()
        print(
            "📸 STRANGER FACE SNAPSHOT SAVED"
        )

        print(
            "File:",
            filepath
        )

        print(
            f"Snapshot size: "
            f"{face_image.width} x "
            f"{face_image.height}"
        )

        print(
            f"Face confidence: "
            f"{stranger_confidence * 100:.2f}%"
        )

        print(
            "Only the detected face region was saved."
        )

        return filepath

    except Exception as e:

        print()
        print(
            "❌ Face snapshot error:"
        )

        print(
            repr(e)
        )

        return None


# ============================================================
# SEND STRANGER ALERT TO TELEGRAM
# ============================================================

def send_stranger_telegram_alert(
    filename,
    stranger_confidence
):

    print()
    print("----------------------------------------")
    print("📱 SENDING STRANGER ALERT TO TELEGRAM")
    print("----------------------------------------")

    # --------------------------------------------------------
    # CHECK CONFIGURATION
    # --------------------------------------------------------

    if (
        BOT_TOKEN == "YOUR_BOT_TOKEN"
        or CHAT_ID == "YOUR_CHAT_ID"
    ):

        print()
        print(
            "❌ Telegram BOT_TOKEN or CHAT_ID "
            "has not been configured."
        )

        print(
            "⚠️ Snapshot remains saved locally."
        )

        return False

    # --------------------------------------------------------
    # CHECK SNAPSHOT
    # --------------------------------------------------------

    if filename is None:

        print(
            "❌ No snapshot file."
        )

        return False

    if not os.path.exists(filename):

        print(
            "❌ Snapshot file does not exist:"
        )

        print(
            filename
        )

        return False

    # --------------------------------------------------------
    # TELEGRAM API
    # --------------------------------------------------------

    url = (
        "https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendPhoto"
    )

    # --------------------------------------------------------
    # LOCAL TIME
    # --------------------------------------------------------

    local_timestamp = (
        formatted_local_time()
    )

    confidence_percent = (
        stranger_confidence * 100.0
    )

    # --------------------------------------------------------
    # TELEGRAM MESSAGE
    # --------------------------------------------------------

    caption = (
        "🚨 SECURITY CAMERA ALERT\n\n"
        "🚨 STRANGER DETECTED\n\n"
        f"Confidence: "
        f"{confidence_percent:.2f}%\n"
        f"Time: {local_timestamp}\n\n"
        "📸 Stranger face snapshot attached."
    )

    try:

        # ----------------------------------------------------
        # OPEN CROPPED FACE IMAGE
        # ----------------------------------------------------

        with open(
            filename,
            "rb"
        ) as photo:

            response = requests.post(
                url,
                data={
                    "chat_id": CHAT_ID,
                    "caption": caption
                },
                files={
                    "photo": photo
                },
                timeout=20
            )

        # ----------------------------------------------------
        # CHECK HTTP RESPONSE
        # ----------------------------------------------------

        if response.ok:

            try:

                result = response.json()

            except Exception:

                result = {}

            if result.get("ok"):

                print()
                print(
                    "✅ Telegram stranger alert "
                    "sent successfully."
                )

                print(
                    "Telegram time:",
                    local_timestamp
                )

                return True

            print()
            print(
                "❌ Telegram returned an error:"
            )

            print(
                result
            )

            return False

        # ----------------------------------------------------
        # HTTP ERROR
        # ----------------------------------------------------

        print()
        print(
            "❌ Telegram HTTP error:"
        )

        print(
            "Status:",
            response.status_code
        )

        print(
            response.text
        )

        return False

    except Exception as e:

        print()
        print(
            "❌ Telegram connection error:"
        )

        print(
            repr(e)
        )

        return False


# ============================================================
# PIR STATE MONITOR
# ============================================================

last_pir_state = 0


def check_pir():

    global last_pir_state
    global pir_active
    global classification_completed_for_motion

    try:

        # ----------------------------------------------------
        # READ PIR THROUGH ROUTERBRIDGE
        # ----------------------------------------------------

        state = Bridge.call(
            "get_pir_state"
        )

        state = int(state)

        # ====================================================
        # MOTION STARTED
        # ====================================================

        if (
            state == 1
            and last_pir_state == 0
        ):

            pir_active = True

            classification_completed_for_motion = False

            print()
            print("=" * 50)
            print("🚨 PIR MOTION DETECTED")
            print("=" * 50)

            print(
                "Motion detected on D8."
            )

            print(
                "👁️ Face detection is now active."
            )

            print(
                "Waiting for a face..."
            )

        # ====================================================
        # MOTION ENDED
        # ====================================================

        elif (
            state == 0
            and last_pir_state == 1
        ):

            pir_active = False

            print()
            print("=" * 50)  # Added separator line
            print(
                "⏳ PIR: no motion"
            )

            print(
                "System is waiting for "
                "the next motion event."
            )
            print("=" * 50)  # Added separator line

        # ----------------------------------------------------
        # SAVE STATE
        # ----------------------------------------------------

        last_pir_state = state

    except Exception as e:

        print()
        print(
            "❌ PIR read error:"
        )

        print(
            repr(e)
        )


# ============================================================
# MAIN LOOP
# ============================================================

def loop():

    check_pir()

    time.sleep(0.1)


# ============================================================
# READY MESSAGE
# ============================================================

print()
print("=" * 50)
print("D-6C TEST READY")
print("=" * 50)

print()
print("PIR pin: D8")

print()
print("WORKFLOW:")
print("PIR D8")
print("↓")
print("MOTION DETECTED")
print("↓")
print("FACE DETECTION")
print("↓")
print("FACE DETECTED")
print("↓")
print("Camera.capture()")
print("↓")
print("ImageClassification")
print("↓")
print("FAMILY / STRANGER")
print("↓")
print("STRANGER → SAVE FACE SNAPSHOT")
print("↓")
print("TELEGRAM ALERT")

print()
print("System is armed.")
print("Waiting for PIR motion...")
print()


# ============================================================
# START APP
# ============================================================

try:

    App.run(
        user_loop=loop
    )

finally:

    try:

        camera.stop()

        print(
            "Camera stopped."
        )

    except Exception:

        pass
