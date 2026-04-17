"""
ai_tracker.py — Real-time Fish Detection Tracker

อ่าน video source จาก env VIDEO_SOURCE:
  VIDEO_SOURCE=0                          → webcam (laptop test)
  VIDEO_SOURCE=fish_video.mp4             → local video file
  VIDEO_SOURCE=rtsp://192.168.x.x:8554/picam → Raspberry Pi via MediaMTX

เริ่มต้น:
  python ai_tracker.py
"""

import cv2
import os
import time
import uuid
import json
import logging
import threading
from ultralytics import YOLO
from flask import Flask, Response
import requests

from video_source import VideoSource

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("ai_tracker")

# ─── Configuration ────────────────────────────────────────────────────────────
BACKEND_URL         = os.getenv("BACKEND_URL",  "http://localhost:8000/api/v1/ai/detect")
SESSION_URL         = os.getenv("SESSION_URL",  "http://localhost:8000/api/v1/sessions")
MODEL_PATH          = os.getenv("MODEL_PATH",   "models/best.pt")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE", "0.4"))
PORT                = int(os.getenv("TRACKER_PORT", "5000"))
API_UPDATE_INTERVAL = float(os.getenv("API_UPDATE_INTERVAL", "1.0"))  # วินาที

# ─── Global State ─────────────────────────────────────────────────────────────
current_frame = None
frame_lock    = threading.Lock()
app           = Flask(__name__)


# ─── Session ──────────────────────────────────────────────────────────────────

def get_or_create_session() -> str:
    """สร้าง session ใหม่ผ่าน backend API"""
    try:
        payload = {
            "location_name": "AI_Auto_Session",
            "notes": f"Session started by AI Tracker — source: {os.getenv('VIDEO_SOURCE', '0')}",
        }
        resp = requests.post(SESSION_URL, json=payload, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            logger.info(f"Session created: {data['id']}")
            return data["id"]
        logger.warning(f"Session API returned {resp.status_code} — using fallback UUID")
    except Exception as e:
        logger.warning(f"Cannot reach session API: {e} — using fallback UUID")
    return str(uuid.uuid4())


# ─── Backend Sync ─────────────────────────────────────────────────────────────

def send_to_backend(payload: dict):
    """ส่งข้อมูล detection ไป backend (fire-and-forget, ไม่บล็อก video thread)"""
    try:
        requests.post(BACKEND_URL, json=payload, timeout=1)
    except Exception:
        pass  # ถ้า backend down ไม่ให้กระทบ video stream


# ─── AI Processing Thread ─────────────────────────────────────────────────────

def ai_processing_thread(session_id: str):
    global current_frame

    # โหลดโมเดล
    logger.info(f"Loading YOLO model: {MODEL_PATH}")
    try:
        model = YOLO(MODEL_PATH)
        # warmup — inference ครั้งแรกจะช้า ให้ทำก่อนรับ stream จริง
        import numpy as np
        model.predict(np.zeros((640, 640, 3), dtype=np.uint8), verbose=False)
        logger.info("Model warmup done")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return

    # เปิด video source
    src = VideoSource.from_env()
    logger.info(f"Opening video source: {src.source_str} (type={src.source_type})")

    if not src.open():
        logger.error(f"Cannot open video source: '{src.source_str}'")
        return

    logger.info(f"Source ready: {src.info()}")

    last_api_update = 0.0

    while True:
        try:
            frame = src.read()
        except RuntimeError as e:
            # webcam disconnect หรือ fatal error
            logger.error(str(e))
            break

        if frame is None:
            # กำลัง reconnect อยู่ (rtsp) หรือ loop file
            continue

        # ─── YOLOv8 Tracking ─────────────────────────────────────────────
        # persist=True คือหัวใจของ ID tracking — ห้ามเอาออก
        results = model.track(frame, persist=True, conf=CONFIDENCE_THRESHOLD, verbose=False)
        result  = results[0]

        annotated = result.plot()

        # อัปเดต frame สำหรับ MJPEG stream
        with frame_lock:
            current_frame = annotated.copy()

        # ─── Sync กับ Backend ────────────────────────────────────────────
        now = time.time()
        if now - last_api_update >= API_UPDATE_INTERVAL:
            last_api_update = now

            if result.boxes and result.boxes.id is not None:
                track_ids = result.boxes.id.int().cpu().tolist()
                classes   = result.boxes.cls.int().cpu().tolist()
                confs     = result.boxes.conf.float().cpu().tolist()
                boxes     = result.boxes.xywh.tolist()

                metadata = [
                    {"track_id": tid, "class": classes[i], "conf": confs[i], "bbox": boxes[i]}
                    for i, tid in enumerate(track_ids)
                ]

                payload = {
                    "session_id":         session_id,
                    "fish_count":         len(track_ids),
                    "track_id":           str(track_ids[0]),
                    "confidence":         confs[0],
                    "fish_type":          result.names.get(classes[0], "Goldfish"),
                    "detection_metadata": metadata,
                }

                threading.Thread(
                    target=send_to_backend,
                    args=(payload,),
                    daemon=True,
                ).start()

    src.release()
    logger.info("AI processing thread stopped")


# ─── Flask MJPEG Streaming ────────────────────────────────────────────────────

def generate_frames():
    """Generator สำหรับ MJPEG stream"""
    while True:
        with frame_lock:
            frame = current_frame

        if frame is None:
            time.sleep(0.05)
            continue

        ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )

        time.sleep(0.033)  # ~30 FPS


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/")
def index():
    source_info = os.getenv("VIDEO_SOURCE", "0")
    return f"""
    <html><body style="background:#0f172a;color:#e2e8f0;font-family:sans-serif;padding:20px">
    <h1>🐟 AI Tracker — Live Stream</h1>
    <p>Source: <code style="color:#06b6d4">{source_info}</code></p>
    <img src="/video_feed" style="max-width:100%;border-radius:8px;border:1px solid #334155">
    </body></html>
    """


@app.route("/health")
def health():
    with frame_lock:
        has_frame = current_frame is not None
    return {"status": "ok", "has_frame": has_frame, "source": os.getenv("VIDEO_SOURCE", "0")}


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    session_id = get_or_create_session()

    # เริ่ม AI thread
    t = threading.Thread(
        target=ai_processing_thread,
        args=(session_id,),
        daemon=True,
        name="ai-processing",
    )
    t.start()

    logger.info(f"Streaming server starting at http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT, threaded=True, debug=False)
