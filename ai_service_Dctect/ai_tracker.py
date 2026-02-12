import cv2
from ultralytics import YOLO
import time
import threading
import queue
from flask import Flask, Response
import requests
import uuid
import json
import os
import atexit

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1/ai/detect"
SESSION_URL = "http://localhost:8000/api/v1/sessions"
VIDEO_SOURCE = "fish_video.mp4" # Or 0 for webcam
MODEL_PATH = "models/best.pt"
CONFIDENCE_THRESHOLD = 0.5
PORT = 5000

# Global State
current_frame = None
lock = threading.Lock()
app = Flask(__name__)

# --- Helper: Create a Session (Optional: Auto-create session on start) ---
def get_or_create_session():
    # For simplicity, we'll create a new session every time the AI starts
    # In production, the Frontend might create the session and pass the ID to the AI
    try:
        payload = {
            "location_name": "AI_Auto_Session",
            "notes": "Session started by AI Tracker script"
        }
        response = requests.post(SESSION_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session Created: {data['id']}")
            return data['id']
    except Exception as e:
        print(f"⚠️ Could not create session: {e}")
        # Fallback to a static UUID for testing if backend is down
        return str(uuid.uuid4())

# --- AI Logic Thread ---
def ai_processing_thread(session_id):
    global current_frame
    
    # Load Model
    print(f"🚀 Loading YOLO Model: {MODEL_PATH}")
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    # Open Video Source
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"❌ Error opening video source: {VIDEO_SOURCE}")
        return

    print("🟢 AI Tracker Started...")
    
    # Memory for API throttling
    last_api_update = 0
    api_update_interval = 1.0 # Send update every 1 second
    
    while True:
        success, frame = cap.read()
        if not success:
            print("End of video stream. Restarting...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Resize for performance (optional)
        # frame = cv2.resize(frame, (640, 480))

        # --- YOLOv8 Tracking ---
        # persist=True is CRITICAL for ID tracking
        results = model.track(frame, persist=True, conf=CONFIDENCE_THRESHOLD, verbose=False)
        result = results[0]
        
        # Visualize
        annotated_frame = result.plot()

        # Update Global Frame for Streaming
        with lock:
            current_frame = annotated_frame.copy()

        # --- Process Detections & Sync with Backend ---
        current_time = time.time()
        if current_time - last_api_update > api_update_interval:
            
            fish_count = 0
            detection_list = []
            
            if result.boxes and result.boxes.id is not None:
                # Extract Track IDs
                track_ids = result.boxes.id.int().cpu().tolist()
                classes = result.boxes.cls.int().cpu().tolist()
                confs = result.boxes.conf.float().cpu().tolist()
                boxes = result.boxes.xywh.tolist()
                
                fish_count = len(track_ids)
                
                # We can send ALL detected fish, or just summary. 
                # Let's send the *first* defined fish as the "primary" detection for the log,
                # OR ideally, the API should accept a LIST. 
                # Since our API strictly defines ONE 'track_id' per row in `FishDetection` (for simplicity in v1),
                # we will loop and send significant updates.
                
                # Strategy: Send the max count and list of IDs in metadata
                # For the 'track_id' field in DB, we serve the "latest" or "most confident" one just to have a value,
                # BUT the `detection_metadata` will hold the real array of all IDs.
                
                metadata = []
                for i, tid in enumerate(track_ids):
                    metadata.append({
                        "track_id": tid,
                        "class": classes[i],
                        "conf": confs[i],
                        "bbox": boxes[i]
                    })
                
                # Construct Payload
                # Note: Sending the "first" track_id as a representative if multiple exist
                primary_track_id = str(track_ids[0]) if track_ids else None
                
                payload = {
                    "session_id": session_id,
                    "fish_count": fish_count,
                    "track_id": primary_track_id, # Can be null if count is 0
                    "confidence": confs[0] if confs else 0.0,
                    "fish_type": "Tilapia", # Replace with class name mapper if needed
                    "detection_metadata": metadata
                }
                
                # Send to Backend (Non-blocking ideally, but requests is fast enough for local)
                try:
                    # Use a separate thread or just fire-and-forget logic to avoid stalling video
                    threading.Thread(target=send_to_backend, args=(payload,)).start()
                except Exception as e:
                    print(f"⚠️ API Error: {e}")
            
            last_api_update = current_time

        # Small sleep? No, let it run as fast as possible for smooth video
    
    cap.release()

def send_to_backend(payload):
    try:
        requests.post(BACKEND_URL, json=payload, timeout=1)
        # print(f"📡 Sent update: Count={payload['fish_count']}")
    except Exception:
        pass # Ignore connection errors during streaming

# --- Flask Video Streaming ---
def generate_frames():
    while True:
        with lock:
            if current_frame is None:
                continue
            
            # Encode frame to JPG
            ret, buffer = cv2.imencode('.jpg', current_frame)
            frame_bytes = buffer.tobytes()
        
        # Yield MJPEG stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.03) # Cap at ~30 FPS

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "<h1>AI Tracker Running...</h1><img src='/video_feed'>"

# --- Main Entry Point ---
if __name__ == '__main__':
    # 1. Get Session ID
    session_id = get_or_create_session()
    
    # 2. Start AI Thread
    t = threading.Thread(target=ai_processing_thread, args=(session_id,))
    t.daemon = True
    t.start()
    
    # 3. Start Flask Server
    print(f"🌍 Streaming Server running at http://0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, threaded=True, debug=False)
