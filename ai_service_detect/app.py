from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from ultralytics import YOLO
import cv2
import numpy as np
import os
import tempfile
import shutil
import subprocess
import threading
import time
from datetime import datetime

from video_source import VideoSource


# ─── Helpers ──────────────────────────────────────────────────────────────────

def convert_to_h264(input_path: str, output_path: str) -> bool:
    """แปลง mp4v → H.264 เพื่อให้ browser เล่นได้"""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", input_path,
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                output_path,
            ],
            capture_output=True,
            check=True,
            timeout=600,
        )
        return True
    except Exception as e:
        print(f"⚠️ ffmpeg convert failed: {e}")
        return False


# ─── Config ───────────────────────────────────────────────────────────────────

CURRENT_DIR      = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH       = os.path.join(CURRENT_DIR, "models", "best.pt")
OUTPUT_DIR       = os.path.join(CURRENT_DIR, "runs", "detect", "api_results")
VIDEO_RESULT_DIR = os.path.join(CURRENT_DIR, "runs", "detect", "video_result")
DEMO_VIDEO       = os.path.join(VIDEO_RESULT_DIR, "output.mp4")
CONFIDENCE       = float(os.getenv("CONFIDENCE", "0.4"))

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─── Live Source State ────────────────────────────────────────────────────────
# background thread อ่าน frame จาก VideoSource และเก็บ frame ล่าสุดไว้
# ให้ /stream/live และ /detect/live เรียกใช้

_live_lock            = threading.Lock()
_live_raw_frame       = None   # frame ดิบ สำหรับ /detect/live
_live_annotated_frame = None   # frame วาด bbox แล้ว สำหรับ /stream/live
_live_source: VideoSource | None = None
_live_thread: threading.Thread | None = None
_live_running         = False


def _live_thread_fn(src: VideoSource):
    """Background thread — อ่าน frame และ run detection ต่อเนื่อง"""
    global _live_raw_frame, _live_annotated_frame, _live_running

    if not src.open():
        print(f"[live] ❌ Cannot open source: '{src.source_str}'")
        return

    print(f"[live] ✅ Source opened: {src.info()}")

    while _live_running:
        try:
            frame = src.read()
        except RuntimeError as e:
            print(f"[live] ❌ {e}")
            break

        if frame is None:
            # กำลัง reconnect (RTSP) หรือ loop file — รอสักครู่
            time.sleep(0.05)
            continue

        # run YOLO detection
        if model is not None:
            results    = model.predict(frame, conf=CONFIDENCE, verbose=False)
            annotated  = results[0].plot()
        else:
            annotated = frame.copy()

        with _live_lock:
            _live_raw_frame       = frame.copy()
            _live_annotated_frame = annotated.copy()

    src.release()
    print("[live] Thread stopped")


def start_live_source():
    global _live_source, _live_thread, _live_running
    _live_running = True
    _live_source  = VideoSource.from_env()
    _live_thread  = threading.Thread(
        target=_live_thread_fn,
        args=(_live_source,),
        daemon=True,
        name="live-source",
    )
    _live_thread.start()
    print(f"[live] Started — VIDEO_SOURCE='{_live_source.source_str}'")


def stop_live_source():
    global _live_running
    _live_running = False
    if _live_thread is not None:
        _live_thread.join(timeout=5)
    print("[live] Stopped")


# ─── Model ────────────────────────────────────────────────────────────────────

model = None
try:
    model = YOLO(MODEL_PATH)
    # warmup: inference dummy frame เพื่อให้ request แรกไม่ช้า
    model.predict(np.zeros((640, 640, 3), dtype=np.uint8), verbose=False)
    print(f"✅ Model loaded & warmed up: {MODEL_PATH}")
except Exception as e:
    print(f"⚠️ Model not loaded: {e}")


# ─── App Lifespan ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_live_source()
    yield
    stop_live_source()


# ─── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="🐟 Tilapia Detection API",
    description="AI Service สำหรับตรวจจับปลานิล (Nile Tilapia) จากภาพ, วิดีโอ และกล้อง live",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Landing Page ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def landing_page():
    has_demo      = os.path.exists(DEMO_VIDEO)
    source_label  = os.getenv("VIDEO_SOURCE", "0")
    source_type   = VideoSource(source_label).source_type if _live_source is None else _live_source.source_type

    source_badge_color = {"webcam": "#22c55e", "rtsp": "#06b6d4", "file": "#f59e0b"}.get(source_type, "#94a3b8")

    demo_section = ""
    if has_demo:
        demo_section = """
        <div class="card">
            <h2>🎬 Demo: AI Fish Detection (recorded)</h2>
            <p style="color:#94a3b8;margin-bottom:16px;">วิดีโอที่ผ่านการตรวจจับปลานิลด้วย YOLOv8 แล้ว</p>
            <video controls autoplay muted loop style="width:100%;border-radius:12px;border:1px solid #334155;">
                <source src="/video/demo" type="video/mp4">
            </video>
        </div>"""
    else:
        demo_section = """
        <div class="card">
            <h2>🎬 Demo Video</h2>
            <p style="color:#f59e0b;">⚠️ ยังไม่มีวิดีโอ demo — ลองรัน <code>python test_video.py</code> ก่อน</p>
        </div>"""

    return f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🐟 Tilapia Detection AI</title>
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: #0f172a; color: #e2e8f0; min-height: 100vh;
            }}
            .container {{ max-width: 960px; margin: 0 auto; padding: 32px 16px; }}
            header {{
                text-align: center; padding: 40px 0 24px;
                border-bottom: 1px solid #1e293b; margin-bottom: 32px;
            }}
            header h1 {{
                font-size: 2rem;
                background: linear-gradient(135deg, #06b6d4, #3b82f6);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }}
            .badge {{
                display: inline-flex; align-items: center; gap: 8px;
                background: #1e293b; padding: 5px 14px; border-radius: 20px;
                font-size: 0.82rem; margin: 4px;
            }}
            .dot {{
                width: 8px; height: 8px; border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}
            .card {{
                background: #1e293b; border: 1px solid #334155;
                border-radius: 16px; padding: 24px; margin-bottom: 24px;
            }}
            .card h2 {{ font-size: 1.15rem; margin-bottom: 10px; }}
            .upload-area {{
                border: 2px dashed #475569; border-radius: 12px;
                padding: 36px; text-align: center; cursor: pointer;
                transition: all 0.3s; margin-top: 16px;
            }}
            .upload-area:hover {{ border-color: #3b82f6; }}
            .upload-area.dragover {{ border-color: #22c55e; background: #1a2332; }}
            input[type="file"] {{ display: none; }}
            .btn {{
                background: linear-gradient(135deg, #06b6d4, #3b82f6);
                color: white; border: none; padding: 10px 28px;
                border-radius: 8px; font-size: 1rem; cursor: pointer;
                margin-top: 14px; transition: transform 0.2s;
            }}
            .btn:hover {{ transform: scale(1.04); }}
            .btn:disabled {{ opacity: 0.5; cursor: not-allowed; transform: none; }}
            .btn-sm {{
                background: #334155; color: #e2e8f0; border: none;
                padding: 7px 18px; border-radius: 6px; font-size: 0.9rem;
                cursor: pointer; transition: background 0.2s;
            }}
            .btn-sm:hover {{ background: #475569; }}
            #result {{ margin-top: 20px; display: none; }}
            #result img, #result video {{ width: 100%; border-radius: 12px; margin-top: 12px; border: 1px solid #334155; }}
            .result-info {{ background: #0f172a; padding: 14px; border-radius: 8px; margin-top: 10px; line-height:1.7; }}
            .loading {{ display: none; text-align: center; padding: 20px; }}
            .spinner {{
                width: 36px; height: 36px; border: 3px solid #334155;
                border-top: 3px solid #3b82f6; border-radius: 50%;
                animation: spin 0.8s linear infinite; margin: 0 auto 10px;
            }}
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
            .links {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }}
            .links a {{
                color: #60a5fa; text-decoration: none; padding: 7px 14px;
                border: 1px solid #334155; border-radius: 8px; transition: all 0.2s;
            }}
            .links a:hover {{ background: #1e293b; border-color: #3b82f6; }}
            #snap-result {{ margin-top: 14px; display: none; }}
            #snap-result img {{ width: 100%; border-radius: 10px; border: 1px solid #334155; }}
        </style>
    </head>
    <body>
    <div class="container">
        <header>
            <h1>🐟 Tilapia Detection AI</h1>
            <p style="color:#94a3b8;">ระบบตรวจจับปลานิล (Nile Tilapia) ด้วย YOLOv8</p>
            <div style="margin-top:12px;">
                <span class="badge">
                    <span class="dot" style="background:{"#22c55e" if model else "#ef4444"}"></span>
                    {"Model Online" if model else "Model Offline"}
                </span>
                <span class="badge">
                    <span class="dot" style="background:{source_badge_color}"></span>
                    Source: {source_label} ({source_type})
                </span>
            </div>
        </header>

        <!-- Live Camera Card -->
        <div class="card">
            <h2>📷 Live Camera — Real-time Detection</h2>
            <p style="color:#94a3b8;margin-bottom:14px;">
                Stream จากกล้องปัจจุบัน (<code style="color:#06b6d4">{source_label}</code>)
                พร้อม AI ตรวจจับปลาแบบ real-time
            </p>
            <img
                id="liveStream"
                src="/stream/live"
                style="width:100%;border-radius:12px;border:1px solid #334155;"
                onerror="this.style.display='none';document.getElementById('streamErr').style.display='block'"
            >
            <div id="streamErr" style="display:none;padding:20px;text-align:center;color:#f59e0b;">
                ⚠️ ไม่สามารถเชื่อมต่อ live stream ได้ — กล้องอาจยังไม่พร้อม
            </div>
            <div style="margin-top:14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
                <button class="btn-sm" onclick="snapFrame()">📸 Snap &amp; Detect</button>
                <button class="btn-sm" onclick="document.getElementById('liveStream').src='/stream/live?t='+Date.now()">🔄 Reconnect</button>
                <span id="snapStatus" style="color:#94a3b8;font-size:0.85rem;"></span>
            </div>
            <div id="snap-result">
                <div class="result-info" id="snapInfo"></div>
                <img id="snapImage" src="" alt="Snap Result">
            </div>
        </div>

        {demo_section}

        <!-- Upload Card -->
        <div class="card">
            <h2>📸🎥 ตรวจจับจากรูปภาพ / วิดีโอ (Upload)</h2>
            <p style="color:#94a3b8;">อัปโหลดรูปหรือวิดีโอปลา แล้ว AI จะตรวจจับและวาดกรอบให้</p>
            <div class="upload-area" id="dropArea" onclick="document.getElementById('fileInput').click()">
                <p style="font-size:2rem;">📁</p>
                <p>คลิกหรือลากไฟล์มาวางที่นี่</p>
                <p style="color:#64748b;font-size:0.85rem;margin-top:8px;">รองรับ JPG, PNG, MP4, AVI, MOV</p>
            </div>
            <input type="file" id="fileInput" accept="image/*,video/*">
            <div style="text-align:center;">
                <button class="btn" id="detectBtn" onclick="detectFile()" disabled>🔍 ตรวจจับ</button>
            </div>
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p id="loadingText">กำลังวิเคราะห์...</p>
            </div>
            <div id="result">
                <div class="result-info" id="resultInfo"></div>
                <img id="resultImage" src="" alt="Detection Result" style="display:none">
                <video id="resultVideo" controls style="display:none;width:100%;border-radius:12px;margin-top:12px;border:1px solid #334155;"></video>
            </div>
        </div>

        <div class="card" style="text-align:center;">
            <h2>🔗 Links</h2>
            <div class="links" style="margin-top:14px;">
                <a href="/docs">📖 API Docs</a>
                <a href="/health">💚 Health</a>
                <a href="/source/status">📡 Source Status</a>
                <a href="https://submarines.app">🏠 Main Site</a>
            </div>
        </div>
    </div>

    <script>
        /* ── Snap & Detect ─────────────────────────────────────── */
        async function snapFrame() {{
            const status = document.getElementById('snapStatus');
            const snapResult = document.getElementById('snap-result');
            const snapInfo = document.getElementById('snapInfo');
            const snapImg = document.getElementById('snapImage');
            status.textContent = '⏳ กำลัง snap...';
            try {{
                const res  = await fetch('/detect/live', {{ method: 'POST' }});
                const data = await res.json();
                if (!res.ok) {{ status.textContent = '❌ ' + (data.detail || 'Error'); return; }}
                snapInfo.innerHTML = data.fish_count === 0
                    ? '<strong>🔍 ไม่พบปลาในเฟรมนี้</strong>'
                    : '<strong>🐟 พบปลา: ' + data.fish_count + ' ตัว</strong><br>'
                      + data.detections.map(d => '• ' + d.class_name + ' (' + (d.confidence*100).toFixed(1) + '%)').join('<br>');
                snapImg.src = data.result_image + '?t=' + Date.now();
                snapResult.style.display = 'block';
                status.textContent = '✅ สำเร็จ';
            }} catch(e) {{ status.textContent = '❌ ' + e.message; }}
        }}

        /* ── Upload File ───────────────────────────────────────── */
        const fileInput = document.getElementById('fileInput');
        const dropArea  = document.getElementById('dropArea');
        const detectBtn = document.getElementById('detectBtn');
        let selectedFile = null;

        function validateFile(file) {{
            const isImg = file.type.startsWith('image/');
            const isVid = file.type.startsWith('video/') || /\.(mp4|avi|mov|mkv)$/i.test(file.name);
            if (!isImg && !isVid) {{
                dropArea.innerHTML = '<p style="font-size:2rem;">⚠️</p><p style="color:#ef4444;">ไม่รองรับไฟล์นี้</p>';
                detectBtn.disabled = true; return false;
            }}
            const icon = isVid ? '🎥' : '🖼️';
            dropArea.innerHTML = '<p style="font-size:2rem;">' + icon + '</p><p>' + file.name + '</p>'
                + '<p style="color:#64748b;font-size:0.8rem;">' + (file.size/1024/1024).toFixed(1) + ' MB</p>';
            detectBtn.disabled = false; return true;
        }}
        fileInput.addEventListener('change', e => {{
            selectedFile = e.target.files[0];
            if (selectedFile && !validateFile(selectedFile)) selectedFile = null;
        }});
        ['dragover','dragenter'].forEach(ev => dropArea.addEventListener(ev, e => {{
            e.preventDefault(); dropArea.classList.add('dragover');
        }}));
        ['dragleave','drop'].forEach(ev => dropArea.addEventListener(ev, e => {{
            e.preventDefault(); dropArea.classList.remove('dragover');
        }}));
        dropArea.addEventListener('drop', e => {{
            selectedFile = e.dataTransfer.files[0];
            if (selectedFile && !validateFile(selectedFile)) selectedFile = null;
        }});

        async function detectFile() {{
            if (!selectedFile) return;
            const loading    = document.getElementById('loading');
            const result     = document.getElementById('result');
            const resultInfo = document.getElementById('resultInfo');
            const resultImg  = document.getElementById('resultImage');
            const resultVid  = document.getElementById('resultVideo');
            const loadTxt    = document.getElementById('loadingText');

            loading.style.display = 'block';
            result.style.display  = 'none';
            resultImg.style.display = 'none';
            resultVid.style.display = 'none';
            detectBtn.disabled = true;

            const isVid = selectedFile.type.startsWith('video/') || /\.(mp4|avi|mov|mkv)$/i.test(selectedFile.name);
            const fd    = new FormData();
            fd.append('file', selectedFile);
            loadTxt.textContent = isVid ? 'กำลังประมวลผลวิดีโอ... อาจใช้เวลาสักครู่ ☕' : 'กำลังวิเคราะห์...';

            try {{
                const endpoint = isVid ? '/detect/video' : '/detect';
                const res = await fetch(endpoint, {{ method: 'POST', body: fd }});
                const ct  = res.headers.get('content-type') || '';
                if (!ct.includes('application/json')) {{
                    resultInfo.innerHTML = '<strong style="color:#ef4444;">❌ Timeout</strong> — ลองใช้ไฟล์เล็กลงหรือเปิด localhost โดยตรง';
                }} else if (!res.ok) {{
                    const data = await res.json();
                    resultInfo.innerHTML = '<strong style="color:#ef4444;">❌ Error:</strong> ' + (data.detail || 'Unknown');
                }} else if (isVid) {{
                    const data = await res.json();
                    resultInfo.innerHTML = '<strong>🎥 ประมวลผลเสร็จ!</strong><br>'
                        + '• Frames: ' + data.total_frames + '<br>'
                        + '• เวลา: ' + data.processing_time + '<br>'
                        + '• พบปลาใน: ' + data.frames_with_fish + ' frames';
                    resultVid.src = data.result_video + '?t=' + Date.now();
                    resultVid.style.display = 'block';
                }} else {{
                    const data = await res.json();
                    resultInfo.innerHTML = data.fish_count === 0
                        ? '<strong>🔍 ไม่พบปลาในภาพ</strong>'
                        : '<strong>🐟 พบปลา: ' + data.fish_count + ' ตัว</strong><br>'
                          + data.detections.map(d => '• ' + d.class_name + ' (' + (d.confidence*100).toFixed(1) + '%)').join('<br>');
                    resultImg.src = data.result_image + '?t=' + Date.now();
                    resultImg.style.display = 'block';
                }}
                result.style.display = 'block';
            }} catch(e) {{
                document.getElementById('result').style.display = 'block';
                document.getElementById('resultInfo').innerHTML = '<strong style="color:#ef4444;">❌ ' + e.message + '</strong>';
            }}
            loading.style.display = 'none';
            detectBtn.disabled = false;
        }}
    </script>
    </body></html>
    """


# ─── Live Stream Endpoints ────────────────────────────────────────────────────

def _mjpeg_generator():
    """Generator สำหรับ MJPEG stream — yield frame ที่ annotated แล้วทุก ~33ms"""
    while True:
        with _live_lock:
            frame = _live_annotated_frame

        if frame is None:
            # ยังไม่มี frame — ส่ง placeholder สีดำ
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, "Waiting for camera...", (120, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
            ret, buf = cv2.imencode(".jpg", blank)
        else:
            ret, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])

        if ret:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buf.tobytes()
                + b"\r\n"
            )

        time.sleep(0.033)  # ~30 FPS


@app.get("/stream/live", summary="MJPEG stream จากกล้อง live พร้อม detection")
def stream_live():
    """
    MJPEG stream จาก VideoSource ปัจจุบัน (webcam / file / RTSP)
    พร้อม bounding box จาก YOLOv8 แบบ real-time

    เปิดใน browser หรือ `<img src="/stream/live">` ได้เลย
    """
    return StreamingResponse(
        _mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.post("/detect/live", summary="Snap 1 frame จากกล้อง live แล้ว detect")
def detect_live():
    """
    ดึง frame ล่าสุดจาก live source → run detection → return ผลลัพธ์

    ไม่ต้องอัปโหลดไฟล์ ใช้ frame จากกล้องที่กำลัง stream อยู่
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model ยังไม่ได้โหลด")

    with _live_lock:
        frame = _live_raw_frame

    if frame is None:
        raise HTTPException(status_code=503, detail="ยังไม่มี frame จาก live source — กล้องยังไม่พร้อม")

    results = model.predict(frame, conf=CONFIDENCE, verbose=False)
    result  = results[0]

    detections = [
        {
            "class":      int(box.cls),
            "class_name": result.names[int(box.cls)],
            "confidence": round(float(box.conf), 4),
            "bbox":       box.xyxy.tolist()[0],
        }
        for box in result.boxes
    ]

    annotated = result.plot()
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:19]
    filename  = f"live_{ts}.jpg"
    cv2.imwrite(os.path.join(OUTPUT_DIR, filename), annotated)

    return {
        "fish_count":  len(detections),
        "detections":  detections,
        "result_image": f"/results/{filename}",
        "source":       os.getenv("VIDEO_SOURCE", "0"),
    }


@app.get("/source/status", summary="สถานะของ live source ปัจจุบัน")
def source_status():
    """ข้อมูล VideoSource ที่กำลังใช้งานอยู่"""
    with _live_lock:
        has_frame = _live_raw_frame is not None

    info = _live_source.info() if _live_source else {"source": "not started", "type": "unknown"}
    return {
        **info,
        "has_frame":  has_frame,
        "confidence": CONFIDENCE,
    }


# ─── Existing Endpoints (unchanged) ──────────────────────────────────────────

@app.get("/video/demo")
def serve_demo_video():
    """สตรีมวิดีโอ demo ที่ผ่านการตรวจจับแล้ว"""
    if not os.path.exists(DEMO_VIDEO):
        raise HTTPException(status_code=404, detail="ยังไม่มีวิดีโอ demo")
    h264_path = DEMO_VIDEO.replace(".mp4", "_h264.mp4")
    if not os.path.exists(h264_path):
        if convert_to_h264(DEMO_VIDEO, h264_path):
            return FileResponse(h264_path, media_type="video/mp4")
    elif os.path.exists(h264_path):
        return FileResponse(h264_path, media_type="video/mp4")
    return FileResponse(DEMO_VIDEO, media_type="video/mp4")


@app.get("/api/status")
def api_status():
    return {
        "service":    "Tilapia Detection AI",
        "version":    "2.0.0",
        "status":     "online" if model else "model_not_loaded",
        "model_path": MODEL_PATH,
        "source":     os.getenv("VIDEO_SOURCE", "0"),
        "docs":       "/docs",
    }


@app.get("/health")
def health():
    with _live_lock:
        has_frame = _live_raw_frame is not None
    return {
        "status":       "ok",
        "model_loaded": model is not None,
        "live_source":  _live_source.source_str if _live_source else None,
        "live_ready":   has_frame,
    }


@app.post("/detect")
async def detect_image(file: UploadFile = File(...), confidence: float = 0.4):
    """อัปโหลดรูปภาพ → AI ตรวจจับปลานิล → return ผลลัพธ์"""
    if not model:
        raise HTTPException(status_code=503, detail="Model ยังไม่ได้โหลด")

    contents = await file.read()
    nparr    = np.frombuffer(contents, np.uint8)
    frame    = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="ไม่สามารถอ่านไฟล์รูปได้")

    results = model.predict(frame, conf=confidence, verbose=False)
    result  = results[0]

    detections = [
        {
            "class":      int(box.cls),
            "class_name": result.names[int(box.cls)],
            "confidence": round(float(box.conf), 4),
            "bbox":       box.xyxy.tolist()[0],
        }
        for box in result.boxes
    ]

    annotated = result.plot()
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"detect_{ts}.jpg"
    cv2.imwrite(os.path.join(OUTPUT_DIR, filename), annotated)

    return {
        "fish_count":  len(detections),
        "detections":  detections,
        "result_image": f"/results/{filename}",
    }


@app.get("/results/{filename}")
def get_result(filename: str):
    """ดึงรูป/วิดีโอผลลัพธ์"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์")
    media = "video/mp4" if filename.endswith(".mp4") else "image/jpeg"
    return FileResponse(filepath, media_type=media)


@app.post("/detect/video")
async def detect_video(file: UploadFile = File(...), confidence: float = 0.4):
    """อัปโหลดวิดีโอ → AI ตรวจจับปลาทีละ frame → return วิดีโอผลลัพธ์"""
    if not model:
        raise HTTPException(status_code=503, detail="Model ยังไม่ได้โหลด")

    tmp_dir   = tempfile.mkdtemp()
    ext       = os.path.splitext(file.filename or ".mp4")[1]
    tmp_input = os.path.join(tmp_dir, f"input{ext}")

    try:
        with open(tmp_input, "wb") as f:
            f.write(await file.read())

        cap = cv2.VideoCapture(tmp_input)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="ไม่สามารถเปิดไฟล์วิดีโอได้")

        fps          = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        ts              = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_path        = os.path.join(OUTPUT_DIR, f"video_{ts}.mp4")
        fourcc          = cv2.VideoWriter_fourcc(*"mp4v")
        writer          = cv2.VideoWriter(raw_path, fourcc, fps, (width, height))

        frame_count      = 0
        frames_with_fish = 0
        start            = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            result = model.predict(frame, conf=confidence, verbose=False)[0]
            if len(result.boxes) > 0:
                frames_with_fish += 1
            writer.write(result.plot())

        cap.release()
        writer.release()

        # แปลงเป็น H.264 เพื่อให้ browser เล่นได้
        h264_path = os.path.join(OUTPUT_DIR, f"video_{ts}_h264.mp4")
        if convert_to_h264(raw_path, h264_path):
            os.remove(raw_path)
            final = f"video_{ts}_h264.mp4"
        else:
            final = f"video_{ts}.mp4"

        elapsed = time.time() - start
        m, s    = int(elapsed // 60), int(elapsed % 60)

        return {
            "total_frames":    total_frames,
            "frames_with_fish": frames_with_fish,
            "processing_time": f"{m}m {s}s" if m else f"{s}s",
            "result_video":    f"/results/{final}",
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
