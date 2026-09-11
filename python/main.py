# from arduino.app_utils import App
# from arduino.app_peripherals.camera import Camera
# from arduino.app_bricks.image_classification import ImageClassification

# import time
# from PIL import Image


# # ============================================================
# # CONFIGURATION
# # ============================================================

# CLASSIFICATION_THRESHOLD = 0.80
# TEST_INTERVAL = 5


# # ============================================================
# # STARTUP
# # ============================================================

# print("================================")
# print("AI SECURITY CAMERA")
# print("CHECKPOINT D-3")
# print("CAMERA + FAMILY CLASSIFICATION")
# print("================================")

# print()
# print("Starting Image Classification...")

# try:
#     image_classification = ImageClassification()

#     print("✅ Image Classification initialized!")

# except Exception as e:

#     print("❌ Image Classification initialization failed:")
#     print(repr(e))

#     App.run()


# print()
# print("Starting USB camera...")

# try:
#     camera = Camera(resolution=(640, 480))
#     camera.start()

#     print("✅ USB camera started successfully!")

# except Exception as e:

#     print("❌ Camera initialization failed:")
#     print(repr(e))

#     App.run()


# print()
# print("================================")
# print("READY")
# print("================================")
# print("Looking at the camera...")
# print("Press Stop in App Lab to end.")
# print()


# # ============================================================
# # CLASSIFICATION FUNCTION
# # ============================================================

# def classify_camera_image():

#     try:

#         print()
#         print("--------------------------------")
#         print("📷 Capturing image...")
#         print("--------------------------------")

#         # Capture image from USB camera
#         frame = camera.capture()

#         if frame is None:

#             print("❌ Camera returned no image.")
#             return

#         print("✅ Image captured.")

#         # ----------------------------------------------------
#         # Convert camera image to PIL Image
#         # ----------------------------------------------------

#         image = Image.fromarray(frame)

#         print(
#             f"Image size: {image.width} x {image.height}"
#         )

#         # ----------------------------------------------------
#         # Run Edge Impulse classification
#         # ----------------------------------------------------

#         print("🧠 Classifying image...")

#         results = image_classification.classify(
#             image,
#             image_type="jpeg",
#             confidence=0.0
#         )

#         print("✅ Classification completed.")

#         if results is None:

#             print("❌ No classification results.")
#             return

#         print()
#         print("================================")
#         print("CLASSIFICATION RESULTS")
#         print("================================")

#         print(results)

#         # ----------------------------------------------------
#         # Read classification results
#         # ----------------------------------------------------

#         classifications = results.get(
#             "classification",
#             []
#         )

#         if not classifications:

#             print()
#             print("⚠️ No classification entries found.")
#             return

#         family_confidence = 0.0
#         stranger_confidence = 0.0

#         print()

#         for item in classifications:

#             class_name = item.get(
#                 "class_name",
#                 "unknown"
#             )

#             raw_confidence = item.get(
#                 "confidence",
#                 0
#             )

#             try:

#                 confidence = float(
#                     raw_confidence
#                 )

#             except (ValueError, TypeError):

#                 confidence = 0.0

#             # Edge Impulse can return either:
#             #
#             # 0.8984
#             #
#             # or:
#             #
#             # 89.84
#             #
#             if confidence > 1.0:

#                 confidence_decimal = (
#                     confidence / 100.0
#                 )

#                 confidence_percent = confidence

#             else:

#                 confidence_decimal = confidence

#                 confidence_percent = (
#                     confidence * 100.0
#                 )

#             print(
#                 f"{class_name}: "
#                 f"{confidence_percent:.2f}%"
#             )

#             # Save confidence values
#             if class_name.lower() == "family":

#                 family_confidence = (
#                     confidence_decimal
#                 )

#             elif class_name.lower() == "stranger":

#                 stranger_confidence = (
#                     confidence_decimal
#                 )

#         # ----------------------------------------------------
#         # Determine result
#         # ----------------------------------------------------

#         print()

#         if family_confidence >= CLASSIFICATION_THRESHOLD:

#             print("================================")
#             print("✅ FAMILY MEMBER")
#             print("================================")

#         elif stranger_confidence >= CLASSIFICATION_THRESHOLD:

#             print("================================")
#             print("🚨 STRANGER DETECTED")
#             print("================================")

#         else:

#             print("================================")
#             print("⚠️ UNCERTAIN")
#             print("================================")

#         print(
#             f"Family confidence: "
#             f"{family_confidence * 100:.2f}%"
#         )

#         print(
#             f"Stranger confidence: "
#             f"{stranger_confidence * 100:.2f}%"
#         )

#     except Exception as e:

#         print()
#         print("================================")
#         print("❌ CLASSIFICATION ERROR")
#         print("================================")

#         print(repr(e))


# # ============================================================
# # MAIN LOOP
# # ============================================================

# try:

#     while True:

#         classify_camera_image()

#         print()
#         print(
#             f"Waiting {TEST_INTERVAL} seconds..."
#         )

#         time.sleep(TEST_INTERVAL)


# except KeyboardInterrupt:

#     print()
#     print("Stopping...")


# except Exception as e:

#     print()
#     print("================================")
#     print("❌ APPLICATION ERROR")
#     print("================================")
#     print(repr(e))


# finally:

#     try:

#         camera.stop()

#         print("✅ Camera stopped.")

#     except Exception:
#         pass










# from arduino.app_utils import App
# from arduino.app_bricks.video_objectdetection import VideoObjectDetection
# from arduino.app_bricks.image_classification import ImageClassification
# from arduino.app_peripherals.camera import Camera

# from PIL import Image
# from datetime import datetime
# import time
# import threading

# # ============================================================
# # CONFIGURATION
# # ============================================================

# FACE_CONFIDENCE = 0.60
# CLASSIFICATION_THRESHOLD = 0.80
# CLASSIFICATION_COOLDOWN = 5
# CAMERA_WIDTH = 640
# CAMERA_HEIGHT = 480

# # ============================================================
# # GLOBAL STATE
# # ============================================================

# last_classification_time = 0
# classification_lock = threading.Lock()
# classification_running = False

# # ============================================================
# # INITIALIZE COMPONENTS
# # ============================================================

# # Image Classification
# print("Initializing Image Classification...")
# image_classification = ImageClassification()
# print("✅ Image Classification initialized!")

# # Camera
# print("Initializing Camera...")
# camera = Camera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT))
# camera.start()
# print("✅ Camera initialized!")

# # Face Detection - Pass the existing camera to avoid conflict
# print("Initializing Face Detection...")
# detection_stream = VideoObjectDetection(
#     camera=camera,  # Pass the existing camera instance
#     confidence=FACE_CONFIDENCE,
#     debounce_sec=1.0
# )
# print("✅ Face Detection initialized!")

# # ============================================================
# # CLASSIFICATION FUNCTION
# # ============================================================

# def classify_current_camera_image():
#     """Capture and classify the current camera image"""
#     global last_classification_time, classification_running
    
#     # Prevent multiple classifications at once
#     with classification_lock:
#         if classification_running:
#             print("⏳ Classification already running.")
#             return
#         classification_running = True
    
#     try:
#         # Cooldown check
#         current_time = time.time()
#         if current_time - last_classification_time < CLASSIFICATION_COOLDOWN:
#             remaining = CLASSIFICATION_COOLDOWN - (current_time - last_classification_time)
#             print(f"⏳ Classification cooldown: {remaining:.1f}s")
#             return
#         last_classification_time = current_time
        
#         # CAPTURE IMAGE (USB Webcam → Camera.capture())
#         print("\n📷 Capturing camera image...")
#         frame = camera.capture()
#         if frame is None:
#             print("❌ Camera returned no image.")
#             return
#         print("✅ Image captured.")
        
#         # Convert to PIL
#         image = Image.fromarray(frame)
#         print(f"Image size: {image.width} x {image.height}")
        
#         # CLASSIFY (ImageClassification)
#         print("\n🧠 Classifying image...")
#         results = image_classification.classify(
#             image,
#             image_type="jpeg",
#             confidence=0.0
#         )
        
#         if results is None:
#             print("❌ Classification returned no results.")
#             return
#         print("✅ Classification completed.")
        
#         # Process classification results
#         classifications = results.get("classification", [])
#         if not classifications:
#             print("⚠️ No classification entries.")
#             return
        
#         family_confidence = 0.0
#         stranger_confidence = 0.0
        
#         print("\n" + "="*40)
#         print("CLASSIFICATION RESULTS")
#         print("="*40)
        
#         for item in classifications:
#             class_name = str(item.get("class_name", "unknown")).lower()
#             raw_confidence = item.get("confidence", 0)
            
#             # Convert confidence to decimal
#             try:
#                 confidence = float(raw_confidence)
#             except (ValueError, TypeError):
#                 confidence = 0.0
            
#             # Handle both 0.9394 and 93.94 formats
#             if confidence > 1.0:
#                 confidence_decimal = confidence / 100.0
#                 confidence_percent = confidence
#             else:
#                 confidence_decimal = confidence
#                 confidence_percent = confidence * 100.0
            
#             print(f"{class_name}: {confidence_percent:.2f}%")
            
#             # Save class confidence
#             if class_name == "family":
#                 family_confidence = confidence_decimal
#             elif class_name == "stranger":
#                 stranger_confidence = confidence_decimal
        
#         # FINAL DECISION
#         print("\n" + "="*40)
#         print("FINAL DECISION")
#         print("="*40)
        
#         # FAMILY
#         if (family_confidence >= CLASSIFICATION_THRESHOLD and 
#             family_confidence > stranger_confidence):
#             print("\n✅ FAMILY MEMBER")
#             print(f"Family confidence: {family_confidence * 100:.2f}%")
#             print(f"Stranger confidence: {stranger_confidence * 100:.2f}%")
        
#         # STRANGER
#         elif (stranger_confidence >= CLASSIFICATION_THRESHOLD and 
#               stranger_confidence > family_confidence):
#             print("\n🚨 STRANGER DETECTED")
#             print(f"Family confidence: {family_confidence * 100:.2f}%")
#             print(f"Stranger confidence: {stranger_confidence * 100:.2f}%")
        
#         # UNCERTAIN
#         else:
#             print("\n⚠️ UNCERTAIN")
#             print(f"Family confidence: {family_confidence * 100:.2f}%")
#             print(f"Stranger confidence: {stranger_confidence * 100:.2f}%")
        
#         print("="*40)
    
#     except Exception as e:
#         print("\n" + "="*40)
#         print("❌ CLASSIFICATION ERROR")
#         print("="*40)
#         print(repr(e))
    
#     finally:
#         classification_running = False

# # ============================================================
# # FACE DETECTED CALLBACK
# # ============================================================

# def face_detected():
#     """Callback when face is detected"""
#     print("\n" + "="*40)
#     print("👤 FACE DETECTED")
#     print("="*40)
#     print(f"Time: {datetime.now().strftime('%B %d, %Y at %I:%M:%S %p')}")
#     print("🧠 Starting family/stranger classification...")
    
#     # Run classification in separate thread (non-blocking)
#     thread = threading.Thread(
#         target=classify_current_camera_image,
#         daemon=True
#     )
#     thread.start()

# # ============================================================
# # REGISTER FACE DETECTION
# # ============================================================

# # USB Webcam → VideoObjectDetection → FACE DETECTED → callback
# detection_stream.on_detect("face", face_detected)

# # ============================================================
# # START APP
# # ============================================================

# print("\n" + "="*40)
# print("AI SECURITY CAMERA")
# print("WORKFLOW: USB Webcam → Face Detection → Classification")
# print("="*40)
# print("\nShow your face to the camera.")
# print("Press Ctrl+C to stop.\n")

# try:
#     App.run()
# except KeyboardInterrupt:
#     print("\nStopping application...")
# finally:
#     try:
#         camera.stop()
#         print("✅ Camera stopped.")
#     except Exception:
#         pass


















# from arduino.app_utils import App, Bridge
# from arduino.app_bricks.video_objectdetection import VideoObjectDetection
# from arduino.app_bricks.image_classification import ImageClassification
# from arduino.app_peripherals.camera import Camera

# from PIL import Image
# from datetime import datetime
# import time
# import threading


# # ============================================================
# # CONFIGURATION
# # ============================================================

# PIR_PIN = "D8"

# FACE_CONFIDENCE = 0.60

# CLASSIFICATION_THRESHOLD = 0.80

# CAMERA_WIDTH = 640
# CAMERA_HEIGHT = 480

# # Minimum time between classifications
# CLASSIFICATION_COOLDOWN = 5.0

# # How often Python checks the PIR
# PIR_POLL_INTERVAL = 0.10

# # After motion starts, give the camera/face detector time
# # to find a face.
# FACE_WAIT_TIMEOUT = 10.0

# # Don't classify repeatedly during the same motion event.
# MOTION_COOLDOWN = 10.0


# # ============================================================
# # GLOBAL STATE
# # ============================================================

# pir_previous_state = 0

# motion_active = False

# face_detected_during_motion = False

# classification_running = False

# last_classification_time = 0.0

# last_motion_time = 0.0

# classification_lock = threading.Lock()

# state_lock = threading.Lock()


# # ============================================================
# # STARTUP
# # ============================================================

# print()
# print("=" * 60)
# print("AI SECURITY CAMERA")
# print("CHECKPOINT D-5")
# print("PIR + FACE + FAMILY / STRANGER")
# print("=" * 60)

# print()
# print("Configuration:")
# print(f"PIR: {PIR_PIN}")
# print(f"Face confidence: {FACE_CONFIDENCE}")
# print(f"Classification threshold: {CLASSIFICATION_THRESHOLD}")
# print(f"Camera: {CAMERA_WIDTH} x {CAMERA_HEIGHT}")

# print()
# print("Initializing Image Classification...")

# try:

#     image_classification = ImageClassification()

#     print("✅ Image Classification initialized!")

# except Exception as e:

#     print("❌ Image Classification initialization failed:")
#     print(repr(e))

#     raise


# # ============================================================
# # CAMERA
# # ============================================================

# print()
# print("Initializing Camera...")

# try:

#     camera = Camera(
#         resolution=(CAMERA_WIDTH, CAMERA_HEIGHT)
#     )

#     camera.start()

#     print("✅ Camera initialized!")

# except Exception as e:

#     print("❌ Camera initialization failed:")
#     print(repr(e))

#     raise


# # ============================================================
# # FACE DETECTION
# # ============================================================

# print()
# print("Initializing Face Detection...")

# try:

#     detection_stream = VideoObjectDetection(
#         camera=camera,
#         confidence=FACE_CONFIDENCE,
#         debounce_sec=1.0
#     )

#     print("✅ Face Detection initialized!")

# except Exception as e:

#     print("❌ Face Detection initialization failed:")
#     print(repr(e))

#     raise


# # ============================================================
# # CLASSIFICATION
# # ============================================================

# def classify_current_camera_image():

#     global classification_running
#     global last_classification_time

#     # --------------------------------------------------------
#     # Prevent simultaneous classifications
#     # --------------------------------------------------------

#     with classification_lock:

#         if classification_running:

#             print("⏳ Classification already running.")

#             return

#         classification_running = True

#     try:

#         # ----------------------------------------------------
#         # Classification cooldown
#         # ----------------------------------------------------

#         now = time.time()

#         if (
#             now - last_classification_time
#             < CLASSIFICATION_COOLDOWN
#         ):

#             remaining = (
#                 CLASSIFICATION_COOLDOWN
#                 - (now - last_classification_time)
#             )

#             print(
#                 f"⏳ Classification cooldown: "
#                 f"{remaining:.1f}s"
#             )

#             return

#         last_classification_time = now


#         # ----------------------------------------------------
#         # Capture image
#         # ----------------------------------------------------

#         print()
#         print("----------------------------------------")
#         print("📷 CAPTURING CAMERA IMAGE")
#         print("----------------------------------------")

#         frame = camera.capture()

#         if frame is None:

#             print("❌ Camera returned no image.")

#             return

#         print("✅ Image captured.")

#         image = Image.fromarray(frame)

#         print(
#             f"Image size: "
#             f"{image.width} x {image.height}"
#         )


#         # ----------------------------------------------------
#         # Classification
#         # ----------------------------------------------------

#         print()
#         print("🧠 Running Family/Stranger classification...")

#         results = image_classification.classify(
#             image,
#             image_type="jpeg",
#             confidence=0.0
#         )

#         if results is None:

#             print("❌ Classification returned no results.")

#             return

#         print("✅ Classification completed.")


#         # ----------------------------------------------------
#         # Extract results
#         # ----------------------------------------------------

#         classifications = results.get(
#             "classification",
#             []
#         )

#         if not classifications:

#             print("⚠️ No classification entries.")

#             return


#         family_confidence = 0.0
#         stranger_confidence = 0.0


#         print()
#         print("=" * 40)
#         print("CLASSIFICATION RESULTS")
#         print("=" * 40)


#         for item in classifications:

#             class_name = str(
#                 item.get(
#                     "class_name",
#                     "unknown"
#                 )
#             ).lower().strip()


#             raw_confidence = item.get(
#                 "confidence",
#                 0
#             )


#             try:

#                 confidence = float(
#                     raw_confidence
#                 )

#             except (ValueError, TypeError):

#                 confidence = 0.0


#             # ------------------------------------------------
#             # Edge Impulse may return:
#             #
#             # 0.9394
#             #
#             # OR
#             #
#             # 93.94
#             # ------------------------------------------------

#             if confidence > 1.0:

#                 confidence_decimal = (
#                     confidence / 100.0
#                 )

#                 confidence_percent = confidence

#             else:

#                 confidence_decimal = confidence

#                 confidence_percent = (
#                     confidence * 100.0
#                 )


#             print(
#                 f"{class_name}: "
#                 f"{confidence_percent:.2f}%"
#             )


#             if class_name == "family":

#                 family_confidence = (
#                     confidence_decimal
#                 )

#             elif class_name == "stranger":

#                 stranger_confidence = (
#                     confidence_decimal
#                 )


#         # ----------------------------------------------------
#         # FINAL DECISION
#         # ----------------------------------------------------

#         print()
#         print("=" * 40)
#         print("FINAL DECISION")
#         print("=" * 40)


#         # FAMILY

#         if (
#             family_confidence
#             >= CLASSIFICATION_THRESHOLD
#             and
#             family_confidence
#             > stranger_confidence
#         ):

#             print()
#             print("🟢 FAMILY MEMBER")

#             print(
#                 f"Family confidence: "
#                 f"{family_confidence * 100:.2f}%"
#             )

#             print(
#                 f"Stranger confidence: "
#                 f"{stranger_confidence * 100:.2f}%"
#             )


#         # STRANGER

#         elif (
#             stranger_confidence
#             >= CLASSIFICATION_THRESHOLD
#             and
#             stranger_confidence
#             > family_confidence
#         ):

#             print()
#             print("🚨 STRANGER DETECTED")

#             print(
#                 f"Family confidence: "
#                 f"{family_confidence * 100:.2f}%"
#             )

#             print(
#                 f"Stranger confidence: "
#                 f"{stranger_confidence * 100:.2f}%"
#             )


#         # UNCERTAIN

#         else:

#             print()
#             print("⚠️ UNCERTAIN")

#             print(
#                 f"Family confidence: "
#                 f"{family_confidence * 100:.2f}%"
#             )

#             print(
#                 f"Stranger confidence: "
#                 f"{stranger_confidence * 100:.2f}%"
#             )


#         print("=" * 40)


#     except Exception as e:

#         print()
#         print("=" * 40)
#         print("❌ CLASSIFICATION ERROR")
#         print("=" * 40)

#         print(repr(e))


#     finally:

#         classification_running = False


# # ============================================================
# # FACE DETECTED CALLBACK
# # ============================================================

# def face_detected():

#     global face_detected_during_motion

#     with state_lock:

#         if not motion_active:

#             return

#         if face_detected_during_motion:

#             return

#         face_detected_during_motion = True


#     print()
#     print("=" * 50)
#     print("👤 FACE DETECTED")
#     print("=" * 50)

#     print(
#         "Time:",
#         datetime.now().strftime(
#             "%B %d, %Y at %I:%M:%S %p"
#         )
#     )

#     print(
#         "Face detected after PIR motion."
#     )

#     print(
#         "➡️ Capturing image for classification..."
#     )


#     # --------------------------------------------------------
#     # Run classification in separate thread
#     # --------------------------------------------------------

#     thread = threading.Thread(
#         target=classify_current_camera_image,
#         daemon=True
#     )

#     thread.start()


# # ============================================================
# # REGISTER FACE DETECTION
# # ============================================================

# detection_stream.on_detect(
#     "face",
#     face_detected
# )


# # ============================================================
# # PIR MONITOR
# # ============================================================

# def pir_monitor():

#     global pir_previous_state
#     global motion_active
#     global face_detected_during_motion
#     global last_motion_time


#     print()
#     print("=" * 50)
#     print("PIR MONITOR READY")
#     print("=" * 50)

#     print(f"PIR pin: {PIR_PIN}")

#     print()
#     print("WORKFLOW:")
#     print("PIR D8")
#     print("↓")
#     print("MOTION DETECTED")
#     print("↓")
#     print("FACE DETECTION")
#     print("↓")
#     print("FACE DETECTED")
#     print("↓")
#     print("Camera.capture()")
#     print("↓")
#     print("ImageClassification")
#     print("↓")
#     print("FAMILY / STRANGER")

#     print()
#     print("System is armed.")
#     print("Waiting for PIR motion...")
#     print()


#     while True:

#         try:

#             # ------------------------------------------------
#             # Read PIR through RouterBridge
#             # ------------------------------------------------

#             state = Bridge.call(
#                 "get_pir_state"
#             )

#             state = int(state)


#             # ------------------------------------------------
#             # LOW → HIGH
#             # New motion event
#             # ------------------------------------------------

#             if (
#                 state == 1
#                 and pir_previous_state == 0
#             ):

#                 now = time.time()

#                 # Ignore extremely close events
#                 if (
#                     now - last_motion_time
#                     >= MOTION_COOLDOWN
#                 ):

#                     last_motion_time = now

#                     with state_lock:

#                         motion_active = True

#                         face_detected_during_motion = False


#                     print()
#                     print("=" * 50)
#                     print("🚨 PIR MOTION DETECTED")
#                     print("=" * 50)

#                     print(
#                         "Motion detected on D8."
#                     )

#                     print(
#                         "👁️ Face detection is now active."
#                     )

#                     print(
#                         "Waiting for a face..."
#                     )

#                     print()


#             # ------------------------------------------------
#             # HIGH → LOW
#             # Motion ended
#             # ------------------------------------------------

#             elif (
#                 state == 0
#                 and pir_previous_state == 1
#             ):

#                 with state_lock:

#                     motion_active = False

#                     face_detected_during_motion = False


#                 print()
#                 print("----------------------------------------")
#                 print("PIR: MOTION ENDED")
#                 print("----------------------------------------")

#                 print(
#                     "System is waiting for the next motion event."
#                 )

#                 print()


#             pir_previous_state = state


#             time.sleep(
#                 PIR_POLL_INTERVAL
#             )


#         except Exception as e:

#             print(
#                 "❌ PIR read error:",
#                 repr(e)
#             )

#             time.sleep(1)


# # ============================================================
# # START PIR MONITOR
# # ============================================================

# pir_thread = threading.Thread(
#     target=pir_monitor,
#     daemon=True
# )

# pir_thread.start()


# # ============================================================
# # START APP
# # ============================================================

# print()
# print("=" * 50)
# print("D-5 TEST READY")
# print("=" * 50)

# print()
# print("USB webcam:")
# print("Camera → VideoObjectDetection")

# print()
# print("PIR:")
# print("D8 → RouterBridge")

# print()
# print("Complete workflow:")
# print(
#     "PIR → FACE → CAPTURE → "
#     "CLASSIFICATION → FAMILY/STRANGER"
# )

# print()
# print("Press Stop in App Lab to stop.")
# print()


# try:

#     App.run()


# except KeyboardInterrupt:

#     print()
#     print("Stopping application...")


# finally:

#     try:

#         camera.stop()

#         print("✅ Camera stopped.")

#     except Exception:

#         pass




































# from arduino.app_utils import App
# from arduino.app_bricks.video_objectdetection import VideoObjectDetection
# from arduino.app_bricks.image_classification import ImageClassification
# from arduino.app_peripherals.camera import Camera

# from PIL import Image
# from datetime import datetime
# import time
# import threading
# import os

# # ============================================================
# # AI SECURITY CAMERA
# # CHECKPOINT D-6A
# # PIR + FACE + FAMILY/STRANGER + EVENT LOGGING
# # ============================================================

# # ============================================================
# # TIMEZONE CONFIGURATION
# # ============================================================

# # Set your timezone to US Eastern
# # US Eastern Time (EDT/EST)
# YOUR_TIMEZONE = "America/New_York"  # US Eastern Time

# # ============================================================
# # TIME FORMAT CONFIGURATION
# # ============================================================

# # Use 12-hour format with AM/PM
# # Format: 2025-01-15 02:30:45 PM
# TIME_FORMAT = "%Y-%m-%d %I:%M:%S %p"

# # Alternative 12-hour formats (uncomment to use):
# # TIME_FORMAT = "%I:%M:%S %p"           # 02:30:45 PM
# # TIME_FORMAT = "%Y-%m-%d %I:%M %p"     # 2025-01-15 02:30 PM
# # TIME_FORMAT = "%b %d, %Y %I:%M:%S %p" # Jan 15, 2025 02:30:45 PM
# # TIME_FORMAT = "%m/%d/%Y %I:%M:%S %p"  # 01/15/2025 02:30:45 PM

# # ============================================================
# # CONFIGURATION
# # ============================================================

# PIR_PIN = 8

# FACE_CONFIDENCE = 0.60

# CLASSIFICATION_THRESHOLD = 0.80

# CLASSIFICATION_COOLDOWN = 5

# CAMERA_WIDTH = 640
# CAMERA_HEIGHT = 480

# PIR_POLL_INTERVAL = 0.10

# # How long the system waits for a face after PIR motion.
# FACE_WAIT_TIMEOUT = 10

# # Folder for D-6A event log.
# LOG_FOLDER = "security_logs"

# LOG_FILE = os.path.join(
#     LOG_FOLDER,
#     "security_events.log"
# )

# # ============================================================
# # CREATE LOG DIRECTORY
# # ============================================================

# try:
#     os.makedirs(LOG_FOLDER, exist_ok=True)
# except Exception as e:
#     print("⚠️ Could not create log directory:")
#     print(repr(e))

# # ============================================================
# # GLOBAL STATE
# # ============================================================

# last_classification_time = 0
# classification_lock = threading.Lock()
# classification_running = False
# system_armed = False
# waiting_for_face = False
# motion_event_active = False
# last_pir_state = None
# face_wait_start = 0

# # ============================================================
# # EVENT LOGGER (UPDATED WITH 12-HOUR TIMEZONE)
# # ============================================================

# def log_event(message):
#     """
#     Write a timestamped event to:
#         1. Python console
#         2. security_logs/security_events.log
#     """
#     try:
#         # Try to use pytz for timezone conversion
#         try:
#             import pytz
#             utc_now = datetime.now(pytz.UTC)
#             local_tz = pytz.timezone(YOUR_TIMEZONE)
#             local_time = utc_now.astimezone(local_tz)
#         except ImportError:
#             # Fallback: use system local time
#             local_time = datetime.now()
        
#         # Use 12-hour format with AM/PM
#         timestamp = local_time.strftime(TIME_FORMAT)
        
#         log_line = f"[{timestamp}] {message}"
        
#         # Console
#         print(log_line)
        
#         # File
#         try:
#             with open(LOG_FILE, "a", encoding="utf-8") as file:
#                 file.write(log_line + "\n")
#         except Exception as e:
#             print("⚠️ Log file write failed:")
#             print(repr(e))
            
#     except Exception as e:
#         # Ultimate fallback
#         timestamp = datetime.now().strftime(TIME_FORMAT)
#         log_line = f"[{timestamp}] {message}"
#         print(log_line)
#         try:
#             with open(LOG_FILE, "a", encoding="utf-8") as file:
#                 file.write(log_line + "\n")
#         except Exception:
#             pass

# # ============================================================
# # STARTUP
# # ============================================================

# print()
# print("=" * 60)
# print("AI SECURITY CAMERA")
# print("CHECKPOINT D-6A")
# print("PIR + FACE + FAMILY / STRANGER")
# print("EVENT LOGGING")
# print(f"TIMEZONE: {YOUR_TIMEZONE}")
# print(f"TIME FORMAT: 12-HOUR (AM/PM)")
# print("=" * 60)
# print()

# # ============================================================
# # INITIALIZE IMAGE CLASSIFICATION
# # ============================================================

# print("Initializing Image Classification...")

# try:
#     image_classification = ImageClassification()
#     print("✅ Image Classification initialized!")
# except Exception as e:
#     print("❌ Image Classification initialization failed:")
#     print(repr(e))
#     raise

# # ============================================================
# # INITIALIZE CAMERA
# # ============================================================

# print()
# print("Initializing Camera...")

# try:
#     camera = Camera(
#         resolution=(
#             CAMERA_WIDTH,
#             CAMERA_HEIGHT
#         )
#     )
#     camera.start()
#     print("✅ Camera initialized!")
# except Exception as e:
#     print("❌ Camera initialization failed:")
#     print(repr(e))
#     raise

# # ============================================================
# # INITIALIZE FACE DETECTION
# # ============================================================

# print()
# print("Initializing Face Detection...")

# try:
#     detection_stream = VideoObjectDetection(
#         camera=camera,
#         confidence=FACE_CONFIDENCE,
#         debounce_sec=1.0
#     )
#     print("✅ Face Detection initialized!")
# except Exception as e:
#     print("❌ Face Detection initialization failed:")
#     print(repr(e))
#     try:
#         camera.stop()
#     except Exception:
#         pass
#     raise

# # ============================================================
# # CLASSIFICATION FUNCTION
# # ============================================================

# def classify_current_camera_image():
#     global last_classification_time
#     global classification_running

#     # --------------------------------------------------------
#     # Prevent multiple classifications
#     # --------------------------------------------------------

#     with classification_lock:
#         if classification_running:
#             print("⏳ Classification already running.")
#             return
#         classification_running = True

#     try:
#         # ----------------------------------------------------
#         # CLASSIFICATION COOLDOWN
#         # ----------------------------------------------------

#         current_time = time.time()
#         elapsed = current_time - last_classification_time

#         if elapsed < CLASSIFICATION_COOLDOWN:
#             remaining = CLASSIFICATION_COOLDOWN - elapsed
#             print(f"⏳ Classification cooldown: {remaining:.1f}s")
#             return

#         last_classification_time = current_time

#         # ----------------------------------------------------
#         # CAPTURE IMAGE
#         # ----------------------------------------------------

#         print()
#         print("----------------------------------------")
#         print("📷 CAPTURING CAMERA IMAGE")
#         print("----------------------------------------")

#         frame = camera.capture()

#         if frame is None:
#             print("❌ Camera returned no image.")
#             log_event("CAMERA ERROR - no image returned")
#             return

#         print("✅ Image captured.")

#         # ----------------------------------------------------
#         # CONVERT TO PIL
#         # ----------------------------------------------------

#         image = Image.fromarray(frame)
#         print(f"Image size: {image.width} x {image.height}")

#         # ----------------------------------------------------
#         # CLASSIFY IMAGE
#         # ----------------------------------------------------

#         print("🧠 Running Family/Stranger classification...")

#         results = image_classification.classify(
#             image,
#             image_type="jpeg",
#             confidence=0.0
#         )

#         if results is None:
#             print("❌ Classification returned no results.")
#             log_event("CLASSIFICATION ERROR - no results")
#             return

#         print("✅ Classification completed.")

#         # ----------------------------------------------------
#         # READ RESULTS
#         # ----------------------------------------------------

#         classifications = results.get("classification", [])

#         if not classifications:
#             print("⚠️ No classification entries.")
#             log_event("CLASSIFICATION - no entries")
#             return

#         family_confidence = 0.0
#         stranger_confidence = 0.0

#         print()
#         print("=" * 40)
#         print("CLASSIFICATION RESULTS")
#         print("=" * 40)

#         # ----------------------------------------------------
#         # PROCESS EACH CLASS
#         # ----------------------------------------------------

#         for item in classifications:
#             class_name = str(item.get("class_name", "unknown")).lower()
#             raw_confidence = item.get("confidence", 0)

#             # ----------------------------------------------
#             # Convert confidence safely
#             # ----------------------------------------------

#             try:
#                 confidence = float(raw_confidence)
#             except (ValueError, TypeError):
#                 confidence = 0.0

#             # ----------------------------------------------
#             # Edge Impulse may return:
#             #
#             # 0.9942
#             #
#             # OR
#             #
#             # 99.42
#             # ----------------------------------------------

#             if confidence > 1.0:
#                 confidence_decimal = confidence / 100.0
#                 confidence_percent = confidence
#             else:
#                 confidence_decimal = confidence
#                 confidence_percent = confidence * 100.0

#             print(f"{class_name}: {confidence_percent:.2f}%")

#             # ----------------------------------------------
#             # Save confidence
#             # ----------------------------------------------

#             if class_name == "family":
#                 family_confidence = confidence_decimal
#             elif class_name == "stranger":
#                 stranger_confidence = confidence_decimal

#         # ----------------------------------------------------
#         # LOG CLASSIFICATION
#         # ----------------------------------------------------

#         log_event(
#             "CLASSIFICATION - "
#             f"family={family_confidence * 100:.2f}% "
#             f"stranger={stranger_confidence * 100:.2f}%"
#         )

#         # ----------------------------------------------------
#         # FINAL DECISION
#         # ----------------------------------------------------

#         print()
#         print("=" * 40)
#         print("FINAL DECISION")
#         print("=" * 40)

#         # ====================================================
#         # FAMILY
#         # ====================================================

#         if (
#             family_confidence >= CLASSIFICATION_THRESHOLD
#             and family_confidence > stranger_confidence
#         ):
#             print()
#             print("🟢 FAMILY MEMBER")
#             print(f"Family confidence: {family_confidence * 100:.2f}%")
#             print(f"Stranger confidence: {stranger_confidence * 100:.2f}%")

#             log_event(
#                 "RESULT - FAMILY MEMBER - "
#                 f"confidence={family_confidence * 100:.2f}%"
#             )

#         # ====================================================
#         # STRANGER
#         # ====================================================

#         elif (
#             stranger_confidence >= CLASSIFICATION_THRESHOLD
#             and stranger_confidence > family_confidence
#         ):
#             print()
#             print("🚨 STRANGER DETECTED")
#             print(f"Family confidence: {family_confidence * 100:.2f}%")
#             print(f"Stranger confidence: {stranger_confidence * 100:.2f}%")

#             log_event(
#                 "RESULT - STRANGER DETECTED - "
#                 f"confidence={stranger_confidence * 100:.2f}%"
#             )

#         # ====================================================
#         # UNCERTAIN
#         # ====================================================

#         else:
#             print()
#             print("⚠️ UNCERTAIN")
#             print(f"Family confidence: {family_confidence * 100:.2f}%")
#             print(f"Stranger confidence: {stranger_confidence * 100:.2f}%")

#             log_event(
#                 "RESULT - UNCERTAIN - "
#                 f"family={family_confidence * 100:.2f}% "
#                 f"stranger={stranger_confidence * 100:.2f}%"
#             )

#         print("=" * 40)

#     except Exception as e:
#         print()
#         print("=" * 40)
#         print("❌ CLASSIFICATION ERROR")
#         print("=" * 40)
#         print(repr(e))
#         log_event("CLASSIFICATION ERROR - " + repr(e))

#     finally:
#         classification_running = False

# # ============================================================
# # FACE DETECTED CALLBACK
# # ============================================================

# def face_detected():
#     global waiting_for_face
#     global system_armed

#     # --------------------------------------------------------
#     # Ignore faces when PIR has not armed the system
#     # --------------------------------------------------------

#     if not system_armed:
#         return

#     # --------------------------------------------------------
#     # Prevent repeated face callbacks
#     # --------------------------------------------------------

#     if not waiting_for_face:
#         return

#     # --------------------------------------------------------
#     # Mark face as handled
#     # --------------------------------------------------------

#     waiting_for_face = False

#     print()
#     print("=" * 50)
#     print("👤 FACE DETECTED")
#     print("=" * 50)
#     print("Face detected after PIR motion.")
#     print("➡️ Capturing image for classification...")

#     log_event("FACE DETECTED after PIR motion")

#     # --------------------------------------------------------
#     # Run classification in separate thread
#     # --------------------------------------------------------

#     thread = threading.Thread(
#         target=classify_current_camera_image,
#         daemon=True
#     )
#     thread.start()

# # ============================================================
# # REGISTER FACE DETECTION
# # ============================================================

# detection_stream.on_detect("face", face_detected)

# # ============================================================
# # PIR READER
# #
# # IMPORTANT:
# #
# # Your UNO Q sketch provides:
# #
# #     get_pir_state
# #
# # through Arduino_RouterBridge.
# #
# # The Python AppController in your App Lab version does NOT
# # have App.call().
# #
# # Therefore, this D-6A code expects the PIR-reading function
# # to be available through the same mechanism you used in the
# # working D-5 PIR code.
# #
# # Replace ONLY the body of read_pir_state() with the exact
# # working PIR call from your D-5 code if necessary.
# # ============================================================

# def read_pir_state():
#     try:
#         # ----------------------------------------------------
#         # This is the RouterBridge function exposed by:
#         #
#         # Bridge.provide("get_pir_state", get_pir_state);
#         #
#         # ----------------------------------------------------

#         # IMPORTANT:
#         # Use the same working RouterBridge access method
#         # from your current D-5 code here.
#         #
#         # This placeholder deliberately does not use:
#         #
#         #     App.call()
#         #
#         # because your diagnostic showed that AppController
#         # has no "call" method.

#         from arduino.app_utils import Bridge
#         return Bridge.call("get_pir_state")

#     except Exception as e:
#         print("❌ PIR read error:")
#         print(repr(e))
#         return None

# # ============================================================
# # PIR MONITOR
# # ============================================================

# def pir_monitor():
#     global system_armed
#     global waiting_for_face
#     global motion_event_active
#     global last_pir_state
#     global face_wait_start

#     print()
#     print("=" * 50)
#     print("PIR MONITOR READY")
#     print("=" * 50)
#     print(f"PIR pin: D{PIR_PIN}")
#     print()
#     print("WORKFLOW:")
#     print("PIR D8")
#     print("↓")
#     print("MOTION DETECTED")
#     print("↓")
#     print("FACE DETECTION")
#     print("↓")
#     print("FACE DETECTED")
#     print("↓")
#     print("Camera.capture()")
#     print("↓")
#     print("ImageClassification")
#     print("↓")
#     print("FAMILY / STRANGER")
#     print()
#     print(f"📄 Event log:")
#     print(LOG_FILE)
#     print(f"⏰ Time format: 12-hour (AM/PM)")
#     print()

#     while True:
#         # ----------------------------------------------------
#         # Read PIR
#         # ----------------------------------------------------

#         state = read_pir_state()

#         if state is None:
#             time.sleep(PIR_POLL_INTERVAL)
#             continue

#         try:
#             state = int(state)
#         except (ValueError, TypeError):
#             time.sleep(PIR_POLL_INTERVAL)
#             continue

#         # ----------------------------------------------------
#         # First PIR reading
#         # ----------------------------------------------------

#         if last_pir_state is None:
#             last_pir_state = state

#         # ====================================================
#         # MOTION STARTED
#         # ====================================================

#         if state == 1 and last_pir_state == 0:
#             print()
#             print("=" * 50)
#             print("🚨 PIR MOTION DETECTED")
#             print("=" * 50)
#             print(f"Motion detected on D{PIR_PIN}.")
#             print("👁️ Face detection is now active.")
#             print("Waiting for a face...")

#             log_event("PIR MOTION DETECTED")

#             system_armed = True
#             waiting_for_face = True
#             motion_event_active = True
#             face_wait_start = time.time()

#         # ====================================================
#         # MOTION ENDED
#         # ====================================================

#         elif state == 0 and last_pir_state == 1:
#             print()
#             print("----------------------------------------")
#             print("⏳ PIR: MOTION ENDED")
#             print("System is waiting for the next motion event.")
#             print("----------------------------------------")

#             log_event("PIR MOTION ENDED")

#             system_armed = False
#             waiting_for_face = False
#             motion_event_active = False

#         # ----------------------------------------------------
#         # Face timeout
#         # ----------------------------------------------------

#         if waiting_for_face and face_wait_start > 0:
#             elapsed = time.time() - face_wait_start

#             if elapsed > FACE_WAIT_TIMEOUT:
#                 print()
#                 print("⏳ Face detection timeout.")
#                 print("No face detected after PIR motion.")

#                 log_event("FACE TIMEOUT - no face detected after PIR motion")

#                 waiting_for_face = False
#                 face_wait_start = 0

#         # ----------------------------------------------------
#         # Save PIR state
#         # ----------------------------------------------------

#         last_pir_state = state

#         time.sleep(PIR_POLL_INTERVAL)

# # ============================================================
# # START PIR MONITOR
# # ============================================================

# pir_thread = threading.Thread(
#     target=pir_monitor,
#     daemon=True
# )
# pir_thread.start()

# # ============================================================
# # APPLICATION START
# # ============================================================

# print()
# print("=" * 60)
# print("D-6A TEST READY")
# print("=" * 60)
# print()
# print("System is armed for PIR → Face → Classification.")
# print()
# print("Event logging is enabled.")
# print(f"Log file: {LOG_FILE}")
# print(f"Timezone: {YOUR_TIMEZONE}")
# print(f"Time format: 12-hour (AM/PM)")
# print()
# print("Waiting for PIR motion...")
# print()

# # ============================================================
# # RUN APP
# # ============================================================

# try:
#     App.run()

# except KeyboardInterrupt:
#     print()
#     print("Stopping application...")

# except Exception as e:
#     print()
#     print("=" * 50)
#     print("❌ APPLICATION ERROR")
#     print("=" * 50)
#     print(repr(e))

# finally:
#     try:
#         camera.stop()
#         print("✅ Camera stopped.")
#     except Exception:
#         pass











# from arduino.app_utils import App, Bridge
# from arduino.app_bricks.video_objectdetection import VideoObjectDetection
# from arduino.app_bricks.image_classification import ImageClassification
# from arduino.app_peripherals.camera import Camera

# from PIL import Image
# from datetime import datetime
# import time
# import threading
# import os


# # ============================================================
# # CONFIGURATION
# # ============================================================

# PIR_PIN = 8

# FACE_CONFIDENCE = 0.60
# CLASSIFICATION_THRESHOLD = 0.80

# CAMERA_WIDTH = 640
# CAMERA_HEIGHT = 480

# # Extra area around the face
# FACE_PADDING = 0.40

# SNAPSHOT_FOLDER = "stranger_snapshots"

# # Prevent rapid repeated face callbacks
# FACE_CALLBACK_COOLDOWN = 2.0


# # ============================================================
# # GLOBAL STATE
# # ============================================================

# pir_motion_active = False

# classification_done_for_event = False
# classification_running = False

# snapshot_saved_for_event = False

# last_face_callback_time = 0.0

# latest_face_box = None
# latest_face_confidence = 0.0

# classification_lock = threading.Lock()


# # ============================================================
# # CREATE SNAPSHOT DIRECTORY
# # ============================================================

# os.makedirs(
#     SNAPSHOT_FOLDER,
#     exist_ok=True
# )


# # ============================================================
# # STARTUP
# # ============================================================

# print("=" * 60)
# print("AI SECURITY CAMERA")
# print("CHECKPOINT D-6B")
# print("PIR + FACE + FAMILY / STRANGER")
# print("STRANGER FACE SNAPSHOT")
# print("=" * 60)

# print()
# print("System is starting...")


# # ============================================================
# # IMAGE CLASSIFICATION
# # ============================================================

# print("Initializing Image Classification...")

# image_classification = ImageClassification()

# print("✅ Image Classification initialized!")


# # ============================================================
# # CAMERA
# # ============================================================

# print("Initializing Camera...")

# camera = Camera(
#     resolution=(
#         CAMERA_WIDTH,
#         CAMERA_HEIGHT
#     )
# )

# camera.start()

# print("✅ Camera initialized!")


# # ============================================================
# # FACE DETECTION
# # ============================================================

# print("Initializing Face Detection...")

# detection_stream = VideoObjectDetection(
#     camera=camera,
#     confidence=FACE_CONFIDENCE,
#     debounce_sec=0.5
# )

# print("✅ Face Detection initialized!")


# # ============================================================
# # PIR
# # ============================================================

# def read_pir():

#     try:

#         state = Bridge.call(
#             "get_pir_state"
#         )

#         return int(state)

#     except Exception as e:

#         print(
#             "❌ PIR read error:"
#         )

#         print(repr(e))

#         return None


# # ============================================================
# # DETECTION DATA CALLBACK
# #
# # THIS IS THE IMPORTANT FIX.
# #
# # on_detect_all() gives us the complete detection dictionary,
# # including bounding_box_xyxy.
# # ============================================================

# def receive_detection_data(detections):

#     global latest_face_box
#     global latest_face_confidence

#     if not pir_motion_active:
#         return

#     try:

#         if not isinstance(
#             detections,
#             dict
#         ):
#             return

#         faces = detections.get(
#             "face",
#             []
#         )

#         if not faces:
#             return

#         # ----------------------------------------------------
#         # Select highest-confidence face
#         # ----------------------------------------------------

#         best_face = max(
#             faces,
#             key=lambda item: float(
#                 item.get(
#                     "confidence",
#                     0
#                 )
#             )
#         )

#         confidence = float(
#             best_face.get(
#                 "confidence",
#                 0
#             )
#         )

#         bounding_box = best_face.get(
#             "bounding_box_xyxy"
#         )

#         # ----------------------------------------------------
#         # Store bounding box
#         # ----------------------------------------------------

#         if bounding_box is not None:

#             latest_face_box = (
#                 int(bounding_box[0]),
#                 int(bounding_box[1]),
#                 int(bounding_box[2]),
#                 int(bounding_box[3])
#             )

#             latest_face_confidence = confidence

#             print(
#                 f"Face confidence: "
#                 f"{confidence:.2f}"
#             )

#             print(
#                 f"Face box: "
#                 f"{latest_face_box}"
#             )

#     except Exception as e:

#         print(
#             "⚠️ Detection data error:"
#         )

#         print(repr(e))


# # ============================================================
# # FACE DETECTED CALLBACK
# # ============================================================

# def face_detected():

#     global last_face_callback_time

#     # --------------------------------------------------------
#     # PIR MUST BE ACTIVE
#     # --------------------------------------------------------

#     if not pir_motion_active:

#         return

#     # --------------------------------------------------------
#     # ONLY ONE CLASSIFICATION PER PIR EVENT
#     # --------------------------------------------------------

#     if classification_done_for_event:

#         return

#     # --------------------------------------------------------
#     # CALLBACK COOLDOWN
#     # --------------------------------------------------------

#     now = time.time()

#     if (
#         now - last_face_callback_time
#         < FACE_CALLBACK_COOLDOWN
#     ):

#         return

#     last_face_callback_time = now

#     print()
#     print("=" * 40)
#     print("👤 FACE DETECTED")
#     print("=" * 40)

#     print(
#         "Face detected after PIR motion."
#     )

#     # --------------------------------------------------------
#     # IMPORTANT:
#     #
#     # Wait a tiny amount of time so that on_detect_all()
#     # has an opportunity to update latest_face_box.
#     # --------------------------------------------------------

#     time.sleep(0.10)

#     print(
#         "➡️ Capturing image for classification..."
#     )

#     thread = threading.Thread(
#         target=classify_face,
#         daemon=True
#     )

#     thread.start()


# # ============================================================
# # REGISTER DETECTION CALLBACKS
# # ============================================================

# # This provides the actual bounding box.
# detection_stream.on_detect_all(
#     receive_detection_data
# )

# # This triggers classification.
# detection_stream.on_detect(
#     "face",
#     face_detected
# )


# # ============================================================
# # SAVE STRANGER FACE
# # ============================================================

# def save_stranger_face(
#     frame,
#     face_box,
#     confidence
# ):

#     try:

#         if frame is None:

#             print(
#                 "❌ No camera frame."
#             )

#             return False

#         if face_box is None:

#             print(
#                 "❌ No face bounding box."
#             )

#             return False

#         # ----------------------------------------------------
#         # Convert frame
#         # ----------------------------------------------------

#         image = Image.fromarray(
#             frame
#         )

#         image_width = image.width
#         image_height = image.height

#         # ----------------------------------------------------
#         # Bounding box
#         # ----------------------------------------------------

#         x1, y1, x2, y2 = face_box

#         x1 = int(x1)
#         y1 = int(y1)
#         x2 = int(x2)
#         y2 = int(y2)

#         # ----------------------------------------------------
#         # Clamp to image
#         # ----------------------------------------------------

#         x1 = max(
#             0,
#             min(
#                 x1,
#                 image_width
#             )
#         )

#         y1 = max(
#             0,
#             min(
#                 y1,
#                 image_height
#             )
#         )

#         x2 = max(
#             0,
#             min(
#                 x2,
#                 image_width
#             )
#         )

#         y2 = max(
#             0,
#             min(
#                 y2,
#                 image_height
#             )
#         )

#         if x2 <= x1 or y2 <= y1:

#             print(
#                 "❌ Invalid face box:"
#             )

#             print(
#                 (x1, y1, x2, y2)
#             )

#             return False

#         # ----------------------------------------------------
#         # Face dimensions
#         # ----------------------------------------------------

#         face_width = x2 - x1
#         face_height = y2 - y1

#         print()
#         print(
#             "----------------------------------------"
#         )

#         print(
#             "📐 FACE BOUNDING BOX"
#         )

#         print(
#             "----------------------------------------"
#         )

#         print(
#             f"Original box: "
#             f"{(x1, y1, x2, y2)}"
#         )

#         print(
#             f"Face size: "
#             f"{face_width} x {face_height}"
#         )

#         print(
#             f"Camera size: "
#             f"{image_width} x {image_height}"
#         )

#         # ----------------------------------------------------
#         # Add padding
#         # ----------------------------------------------------

#         pad_x = int(
#             face_width * FACE_PADDING
#         )

#         pad_y = int(
#             face_height * FACE_PADDING
#         )

#         crop_x1 = max(
#             0,
#             x1 - pad_x
#         )

#         crop_y1 = max(
#             0,
#             y1 - pad_y
#         )

#         crop_x2 = min(
#             image_width,
#             x2 + pad_x
#         )

#         crop_y2 = min(
#             image_height,
#             y2 + pad_y
#         )

#         print(
#             f"Crop box: "
#             f"{(crop_x1, crop_y1, crop_x2, crop_y2)}"
#         )

#         # ----------------------------------------------------
#         # Crop
#         # ----------------------------------------------------

#         face_image = image.crop(
#             (
#                 crop_x1,
#                 crop_y1,
#                 crop_x2,
#                 crop_y2
#             )
#         )

#         # ----------------------------------------------------
#         # Filename
#         # ----------------------------------------------------

#         timestamp = datetime.now().strftime(
#             "%Y%m%d_%H%M%S"
#         )

#         confidence_percent = int(
#             confidence * 100
#         )

#         filename = (
#             "stranger_face_"
#             f"{timestamp}_"
#             f"{confidence_percent}pct.jpg"
#         )

#         filepath = os.path.join(
#             SNAPSHOT_FOLDER,
#             filename
#         )

#         # ----------------------------------------------------
#         # Save
#         # ----------------------------------------------------

#         face_image.save(
#             filepath,
#             format="JPEG",
#             quality=95
#         )

#         print()
#         print(
#             "📸 STRANGER FACE SNAPSHOT SAVED"
#         )

#         print(
#             f"File: {filepath}"
#         )

#         print(
#             f"Snapshot size: "
#             f"{face_image.width} x "
#             f"{face_image.height}"
#         )

#         print(
#             f"Face confidence: "
#             f"{confidence * 100:.2f}%"
#         )

#         print(
#             "Only the detected face region was saved."
#         )

#         return True

#     except Exception as e:

#         print(
#             "❌ SNAPSHOT ERROR"
#         )

#         print(repr(e))

#         return False


# # ============================================================
# # CLASSIFICATION
# # ============================================================

# def classify_face():

#     global classification_running
#     global classification_done_for_event
#     global snapshot_saved_for_event

#     with classification_lock:

#         if classification_running:

#             print(
#                 "⏳ Classification already running."
#             )

#             return

#         if classification_done_for_event:

#             print(
#                 "⏭️ Classification already completed "
#                 "for this PIR event."
#             )

#             return

#         classification_running = True

#         # Lock this PIR event immediately.
#         classification_done_for_event = True

#     try:

#         print()
#         print(
#             "----------------------------------------"
#         )

#         print(
#             "📷 CAPTURING CAMERA IMAGE"
#         )

#         print(
#             "----------------------------------------"
#         )

#         # ----------------------------------------------------
#         # Capture
#         # ----------------------------------------------------

#         frame = camera.capture()

#         if frame is None:

#             print(
#                 "❌ Camera returned no image."
#             )

#             classification_done_for_event = False

#             return

#         print(
#             "✅ Image captured."
#         )

#         image = Image.fromarray(
#             frame
#         )

#         print(
#             f"Image size: "
#             f"{image.width} x "
#             f"{image.height}"
#         )

#         # ----------------------------------------------------
#         # Get latest face box
#         # ----------------------------------------------------

#         face_box = latest_face_box

#         if face_box is not None:

#             print(
#                 f"Using face box: "
#                 f"{face_box}"
#             )

#         else:

#             print(
#                 "⚠️ No face bounding box available."
#             )

#         # ----------------------------------------------------
#         # Classification
#         # ----------------------------------------------------

#         print(
#             "🧠 Running Family/Stranger classification..."
#         )

#         results = image_classification.classify(
#             image,
#             image_type="jpeg",
#             confidence=0.0
#         )

#         if results is None:

#             print(
#                 "❌ Classification returned no results."
#             )

#             return

#         print(
#             "✅ Classification completed."
#         )

#         # ----------------------------------------------------
#         # Results
#         # ----------------------------------------------------

#         classifications = results.get(
#             "classification",
#             []
#         )

#         if not classifications:

#             print(
#                 "⚠️ No classification entries."
#             )

#             return

#         family_confidence = 0.0
#         stranger_confidence = 0.0

#         print(
#             "=" * 40
#         )

#         print(
#             "CLASSIFICATION RESULTS"
#         )

#         print(
#             "=" * 40
#         )

#         for item in classifications:

#             class_name = str(
#                 item.get(
#                     "class_name",
#                     "unknown"
#                 )
#             ).lower().strip()

#             raw_confidence = item.get(
#                 "confidence",
#                 0
#             )

#             try:

#                 confidence = float(
#                     raw_confidence
#                 )

#             except (
#                 ValueError,
#                 TypeError
#             ):

#                 confidence = 0.0

#             if confidence > 1.0:

#                 confidence /= 100.0

#             confidence = max(
#                 0.0,
#                 min(
#                     confidence,
#                     1.0
#                 )
#             )

#             print(
#                 f"{class_name}: "
#                 f"{confidence * 100:.2f}%"
#             )

#             if class_name == "family":

#                 family_confidence = confidence

#             elif class_name == "stranger":

#                 stranger_confidence = confidence

#         # ----------------------------------------------------
#         # Decision
#         # ----------------------------------------------------

#         print(
#             "=" * 40
#         )

#         print(
#             "FINAL DECISION"
#         )

#         print(
#             "=" * 40
#         )

#         print(
#             f"Family confidence: "
#             f"{family_confidence * 100:.2f}%"
#         )

#         print(
#             f"Stranger confidence: "
#             f"{stranger_confidence * 100:.2f}%"
#         )

#         # ====================================================
#         # FAMILY
#         # ====================================================

#         if (
#             family_confidence
#             >= CLASSIFICATION_THRESHOLD
#             and
#             family_confidence
#             > stranger_confidence
#         ):

#             print()
#             print(
#                 "🟢 FAMILY MEMBER"
#             )

#             print(
#                 "No snapshot saved."
#             )

#         # ====================================================
#         # STRANGER
#         # ====================================================

#         elif (
#             stranger_confidence
#             >= CLASSIFICATION_THRESHOLD
#             and
#             stranger_confidence
#             > family_confidence
#         ):

#             print()
#             print(
#                 "🚨 STRANGER DETECTED"
#             )

#             print(
#                 f"Stranger confidence: "
#                 f"{stranger_confidence * 100:.2f}%"
#             )

#             if (
#                 not snapshot_saved_for_event
#                 and
#                 face_box is not None
#             ):

#                 print()
#                 print(
#                     "📸 Preparing stranger face snapshot..."
#                 )

#                 saved = save_stranger_face(
#                     frame,
#                     face_box,
#                     stranger_confidence
#                 )

#                 if saved:

#                     snapshot_saved_for_event = True

#                     print(
#                         "✅ Stranger face snapshot completed."
#                     )

#                 else:

#                     print(
#                         "❌ Stranger face snapshot failed."
#                     )

#             elif face_box is None:

#                 print()
#                 print(
#                     "❌ Cannot save snapshot because "
#                     "face bounding box is missing."
#                 )

#             else:

#                 print(
#                     "⏭️ Snapshot already saved "
#                     "for this PIR event."
#                 )

#         # ====================================================
#         # UNCERTAIN
#         # ====================================================

#         else:

#             print()
#             print(
#                 "⚠️ UNCERTAIN"
#             )

#             print(
#                 "No snapshot saved."
#             )

#         print(
#             "=" * 40
#         )

#     except Exception as e:

#         print()
#         print(
#             "❌ CLASSIFICATION ERROR"
#         )

#         print(
#             repr(e)
#         )

#         classification_done_for_event = False

#     finally:

#         classification_running = False


# # ============================================================
# # PIR MONITOR
# # ============================================================

# def pir_monitor():

#     global pir_motion_active
#     global classification_done_for_event
#     global classification_running
#     global snapshot_saved_for_event
#     global latest_face_box
#     global latest_face_confidence
#     global last_face_callback_time

#     print()
#     print("=" * 60)
#     print("PIR MONITOR READY")
#     print("=" * 60)

#     print(
#         f"PIR pin: D{PIR_PIN}"
#     )

#     print()
#     print("WORKFLOW:")
#     print("PIR D8")
#     print("↓")
#     print("MOTION DETECTED")
#     print("↓")
#     print("FACE DETECTION")
#     print("↓")
#     print("FACE DETECTED")
#     print("↓")
#     print("Camera.capture()")
#     print("↓")
#     print("ImageClassification")
#     print("↓")
#     print("FAMILY / STRANGER")
#     print("↓")
#     print("STRANGER → SAVE FACE SNAPSHOT")

#     print()
#     print("System is armed.")
#     print("Waiting for PIR motion...")

#     last_state = 0

#     while True:

#         state = read_pir()

#         if state is None:

#             time.sleep(0.5)

#             continue

#         # ====================================================
#         # PIR LOW → HIGH
#         # ====================================================

#         if (
#             state == 1
#             and
#             last_state == 0
#         ):

#             pir_motion_active = True

#             classification_done_for_event = False
#             classification_running = False

#             snapshot_saved_for_event = False

#             latest_face_box = None
#             latest_face_confidence = 0.0

#             last_face_callback_time = 0.0

#             print()
#             print("=" * 50)
#             print(
#                 "🚨 PIR MOTION DETECTED"
#             )
#             print("=" * 50)

#             print(
#                 "Motion detected on D8."
#             )

#             print(
#                 "👁️ Face detection is now active."
#             )

#             print(
#                 "Waiting for a face..."
#             )

#         # ====================================================
#         # PIR HIGH → LOW
#         # ====================================================

#         elif (
#             state == 0
#             and
#             last_state == 1
#         ):

#             pir_motion_active = False

#             print()
#             print("=" * 50)  # Added separator line
#             print(
#                 "⏳ PIR: no motion"
#             )
            

#             print(
#                 "System is waiting for the next "
#                 "motion event."
#             )
#             print("=" * 50)  # Added separator line
#         last_state = state

#         time.sleep(0.15)


# # ============================================================
# # START PIR THREAD
# # ============================================================

# pir_thread = threading.Thread(
#     target=pir_monitor,
#     daemon=True
# )

# pir_thread.start()


# # ============================================================
# # RUN APP
# # ============================================================

# try:

#     App.run()

# except KeyboardInterrupt:

#     print()
#     print(
#         "Stopping application..."
#     )

# finally:

#     try:

#         camera.stop()

#         print(
#             "✅ Camera stopped."
#         )

#     except Exception:
#         pass












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

# BOT_TOKEN = "8891781087:AAFuvOtBBiqgyS5FZOMTm9WyzZqFjnYV7yM"
# CHAT_ID = "8898500928"

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