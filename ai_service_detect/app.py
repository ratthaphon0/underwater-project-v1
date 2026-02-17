from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from ultralytics import YOLO
import cv2
import numpy as np
import os
import tempfile
import shutil
import subprocess
from datetime import datetime


def convert_to_h264(input_path: str, output_path: str):
    """แปลง mp4v → H.264 เพื่อให้ browser เล่นได้"""
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            output_path
        ], capture_output=True, check=True, timeout=600)
        return True
    except Exception as e:
        print(f"⚠️ ffmpeg convert failed: {e}")
        return False

# --- Config ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, 'models', 'best.pt')
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'runs', 'detect', 'api_results')
VIDEO_RESULT_DIR = os.path.join(CURRENT_DIR, 'runs', 'detect', 'video_result')
DEMO_VIDEO = os.path.join(VIDEO_RESULT_DIR, 'output.mp4')
SOURCE_VIDEOS = [
    os.path.join(CURRENT_DIR, 'fish_video.mp4'),
    os.path.join(CURRENT_DIR, 'fish_video_2.mp4'),
    os.path.join(CURRENT_DIR, 'fish_video_3.mp4'),
    os.path.join(CURRENT_DIR, 'fish_video_4.mp4'),
]
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- App ---
app = FastAPI(
    title="🐟 Tilapia Detection API",
    description="AI Service สำหรับตรวจจับปลานิล (Nile Tilapia) จากภาพหรือวิดีโอ",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- โหลด Model ---
model = None
try:
    model = YOLO(MODEL_PATH)
    print(f"✅ โหลดโมเดลสำเร็จ: {MODEL_PATH}")
except Exception as e:
    print(f"⚠️ โหลดโมเดลไม่ได้: {e}")


# --- HTML Landing Page ---
@app.get("/", response_class=HTMLResponse)
def landing_page():
    has_demo = os.path.exists(DEMO_VIDEO)
    video_section = ""
    if has_demo:
        video_section = """
        <div class="card">
            <h2>🎬 Demo: AI Fish Detection</h2>
            <p style="color:#94a3b8;margin-bottom:16px;">วิดีโอที่ผ่านการตรวจจับปลานิลด้วย YOLOv8 แล้ว</p>
            <video controls autoplay muted loop style="width:100%;border-radius:12px;border:1px solid #334155;">
                <source src="/video/demo" type="video/mp4">
                Browser ไม่รองรับ video
            </video>
        </div>
        """
    else:
        video_section = """
        <div class="card">
            <h2>🎬 Demo Video</h2>
            <p style="color:#f59e0b;">⚠️ ยังไม่มีวิดีโอ demo — ลองรัน <code>python test_video.py</code> ก่อน</p>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🐟 Tilapia Detection AI — submarines.app</title>
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: #0f172a;
                color: #e2e8f0;
                min-height: 100vh;
            }}
            .container {{ max-width: 900px; margin: 0 auto; padding: 32px 16px; }}
            header {{
                text-align: center;
                padding: 40px 0 24px;
                border-bottom: 1px solid #1e293b;
                margin-bottom: 32px;
            }}
            header h1 {{
                font-size: 2rem;
                background: linear-gradient(135deg, #06b6d4, #3b82f6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }}
            header p {{ color: #94a3b8; }}
            .status {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: #1e293b;
                padding: 6px 16px;
                border-radius: 20px;
                font-size: 0.85rem;
                margin-top: 12px;
            }}
            .status .dot {{
                width: 8px; height: 8px;
                border-radius: 50%;
                background: {"#22c55e" if model else "#ef4444"};
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.4; }}
            }}
            .card {{
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 24px;
            }}
            .card h2 {{ font-size: 1.2rem; margin-bottom: 8px; }}
            .upload-area {{
                border: 2px dashed #475569;
                border-radius: 12px;
                padding: 40px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                margin-top: 16px;
            }}
            .upload-area:hover {{ border-color: #3b82f6; background: #1e293b; }}
            .upload-area.dragover {{ border-color: #22c55e; background: #1a2332; }}
            input[type="file"] {{ display: none; }}
            .btn {{
                background: linear-gradient(135deg, #06b6d4, #3b82f6);
                color: white;
                border: none;
                padding: 12px 32px;
                border-radius: 8px;
                font-size: 1rem;
                cursor: pointer;
                margin-top: 16px;
                transition: transform 0.2s;
            }}
            .btn:hover {{ transform: scale(1.05); }}
            .btn:disabled {{ opacity: 0.5; cursor: not-allowed; transform: none; }}
            #result {{ margin-top: 20px; display: none; }}
            #result img {{ width: 100%; border-radius: 12px; margin-top: 12px; border: 1px solid #334155; }}
            .result-info {{ background: #0f172a; padding: 16px; border-radius: 8px; margin-top: 12px; }}
            .links {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }}
            .links a {{
                color: #60a5fa;
                text-decoration: none;
                padding: 8px 16px;
                border: 1px solid #334155;
                border-radius: 8px;
                transition: all 0.2s;
            }}
            .links a:hover {{ background: #1e293b; border-color: #3b82f6; }}
            .loading {{ display: none; text-align: center; padding: 20px; }}
            .spinner {{
                width: 40px; height: 40px;
                border: 3px solid #334155;
                border-top: 3px solid #3b82f6;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin: 0 auto 12px;
            }}
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🐟 Tilapia Detection AI</h1>
                <p>ระบบตรวจจับปลานิล (Nile Tilapia) ด้วย YOLOv8</p>
                <div class="status">
                    <div class="dot"></div>
                    {"Model Online — พร้อมตรวจจับ" if model else "Model Offline"}
                </div>
            </header>

            {video_section}

            <div class="card">
                <h2>📸🎥 ทดสอบตรวจจับจากรูปภาพ / วิดีโอ</h2>
                <p style="color:#94a3b8;">อัปโหลดรูปหรือวิดีโอปลา แล้ว AI จะตรวจจับและวาดกรอบให้</p>
                <div class="upload-area" id="dropArea" onclick="document.getElementById('fileInput').click()">
                    <p style="font-size:2rem;">📁</p>
                    <p>คลิกหรือลากไฟล์มาวางที่นี่</p>
                    <p style="color:#64748b;font-size:0.85rem;margin-top:8px;">รองรับ JPG, PNG, MP4, AVI, MOV</p>
                </div>
                <input type="file" id="fileInput" accept="image/*,video/*">
                <div style="text-align:center;">
                    <button class="btn" id="detectBtn" onclick="detectImage()" disabled>🔍 ตรวจจับ</button>
                </div>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>กำลังวิเคราะห์...</p>
                </div>
                <div id="result">
                    <div class="result-info" id="resultInfo"></div>
                    <img id="resultImage" src="" alt="Detection Result">
                    <video id="resultVideo" controls style="width:100%;border-radius:12px;margin-top:12px;border:1px solid #334155;display:none;"></video>
                </div>
            </div>

            <div class="card" style="text-align:center;">
                <h2>🔗 Links</h2>
                <div class="links" style="margin-top:16px;">
                    <a href="/docs">📖 API Docs</a>
                    <a href="/health">💚 Health Check</a>
                    <a href="https://submarines.app">🏠 Main Site</a>
                </div>
            </div>
        </div>

        <script>
            const fileInput = document.getElementById('fileInput');
            const dropArea = document.getElementById('dropArea');
            const detectBtn = document.getElementById('detectBtn');
            let selectedFile = null;

            function validateFile(file) {{
                const isImage = file.type.startsWith('image/');
                const isVideo = file.type.startsWith('video/') || /\.(mp4|avi|mov|mkv)$/i.test(file.name);
                if (!isImage && !isVideo) {{
                    dropArea.innerHTML = '<p style="font-size:2rem;">⚠️</p><p style="color:#f59e0b;">' + file.name + '</p><p style="color:#ef4444;font-size:0.85rem;">ไม่รองรับไฟล์ประเภทนี้</p>';
                    detectBtn.disabled = true;
                    return false;
                }}
                const icon = isVideo ? '🎥' : '🖼️';
                dropArea.innerHTML = '<p style="font-size:2rem;">' + icon + '</p><p>' + file.name + '</p><p style="color:#64748b;font-size:0.8rem;">' + (isVideo ? 'วิดีโอ' : 'รูปภาพ') + ' — ' + (file.size / 1024 / 1024).toFixed(1) + ' MB</p>';
                detectBtn.disabled = false;
                return true;
            }}

            fileInput.addEventListener('change', (e) => {{
                selectedFile = e.target.files[0];
                if (selectedFile && !validateFile(selectedFile)) selectedFile = null;
            }});

            ['dragover','dragenter'].forEach(ev => {{
                dropArea.addEventListener(ev, (e) => {{ e.preventDefault(); dropArea.classList.add('dragover'); }});
            }});
            ['dragleave','drop'].forEach(ev => {{
                dropArea.addEventListener(ev, (e) => {{ e.preventDefault(); dropArea.classList.remove('dragover'); }});
            }});
            dropArea.addEventListener('drop', (e) => {{
                selectedFile = e.dataTransfer.files[0];
                if (selectedFile && !validateFile(selectedFile)) selectedFile = null;
            }});

            async function detectImage() {{
                if (!selectedFile) return;
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                const resultInfo = document.getElementById('resultInfo');
                const resultImage = document.getElementById('resultImage');
                const resultVideo = document.getElementById('resultVideo');

                loading.style.display = 'block';
                result.style.display = 'none';
                resultImage.style.display = 'none';
                resultVideo.style.display = 'none';
                detectBtn.disabled = true;

                const isVideo = selectedFile.type.startsWith('video/') || /\.(mp4|avi|mov|mkv)$/i.test(selectedFile.name);
                const formData = new FormData();
                formData.append('file', selectedFile);

                try {{
                    const endpoint = isVideo ? '/detect/video' : '/detect';
                    const loadingText = document.querySelector('#loading p');
                    if (isVideo) loadingText.textContent = 'กำลังประมวลผลวิดีโอ... อาจใช้เวลาหลายนาที ☕';
                    else loadingText.textContent = 'กำลังวิเคราะห์...';

                    const res = await fetch(endpoint, {{ method: 'POST', body: formData }});
                    const contentType = res.headers.get('content-type') || '';

                    if (!contentType.includes('application/json')) {{
                        resultInfo.innerHTML = '<strong style=\"color:#ef4444;\">❌ Timeout:</strong> วิดีโอใหญ่เกินไปสำหรับ Tunnel — ลองใช้ <a href=\"http://localhost:8001\" style=\"color:#60a5fa;\">localhost:8001</a> แทน หรือใช้ไฟล์เล็กลง';
                        result.style.display = 'block';
                    }} else if (!res.ok) {{
                        const data = await res.json();
                        resultInfo.innerHTML = '<strong style=\"color:#ef4444;\">❌ Error:</strong> ' + (data.detail || 'Unknown error');
                        result.style.display = 'block';
                    }} else if (isVideo) {{
                        const data = await res.json();
                        resultInfo.innerHTML = '<strong>🎥 ประมวลผลเสร็จ!</strong><br>' +
                            '• ประมวลผล: ' + data.total_frames + ' frames<br>' +
                            '• เวลา: ' + data.processing_time + '<br>' +
                            '• พบปลาใน: ' + data.frames_with_fish + ' frames';
                        resultVideo.src = data.result_video + '?t=' + Date.now();
                        resultVideo.style.display = 'block';
                        result.style.display = 'block';
                    }} else {{
                        const data = await res.json();
                        if (data.fish_count === 0) {{
                            resultInfo.innerHTML = '<strong>🔍 ไม่พบปลาในภาพ</strong>';
                        }} else {{
                            resultInfo.innerHTML = '<strong>🐟 พบปลา: ' + data.fish_count + ' ตัว</strong><br>' +
                                data.detections.map(d => '• ' + d.class_name + ' (confidence: ' + (d.confidence * 100).toFixed(1) + '%)').join('<br>');
                        }}
                        resultImage.src = data.result_image;
                        resultImage.style.display = 'block';
                        result.style.display = 'block';
                    }}
                }} catch (err) {{
                    resultInfo.innerHTML = '<strong style=\"color:#ef4444;\">❌ Error:</strong> ' + err.message;
                    result.style.display = 'block';
                }}

                loading.style.display = 'none';
                detectBtn.disabled = false;
            }}
        </script>
    </body>
    </html>
    """


@app.get("/video/demo")
def serve_demo_video():
    """สตรีมวิดีโอ demo ที่ผ่านการตรวจจับแล้ว (แปลง H.264 อัตโนมัติ)"""
    if not os.path.exists(DEMO_VIDEO):
        raise HTTPException(status_code=404, detail="ยังไม่มีวิดีโอ demo")
    # แปลง H.264 ถ้ายังไม่มี
    h264_path = DEMO_VIDEO.replace('.mp4', '_h264.mp4')
    if not os.path.exists(h264_path):
        print("🔄 กำลังแปลง demo video เป็น H.264...")
        if convert_to_h264(DEMO_VIDEO, h264_path):
            print("✅ แปลง demo video สำเร็จ")
        else:
            return FileResponse(DEMO_VIDEO, media_type="video/mp4")
    return FileResponse(h264_path, media_type="video/mp4")


@app.get("/api/status")
def api_status():
    return {
        "service": "Tilapia Detection AI",
        "status": "online" if model else "model_not_loaded",
        "model_path": MODEL_PATH,
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
    }


@app.post("/detect")
async def detect_image(
    file: UploadFile = File(...),
    confidence: float = 0.25
):
    """
    อัปโหลดรูปภาพ → AI ตรวจจับปลานิล → return ผลลัพธ์

    - **file**: ไฟล์รูปภาพ (jpg, png)
    - **confidence**: ค่า confidence threshold (default: 0.25)
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model ยังไม่ได้โหลด")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=400, detail="ไม่สามารถอ่านไฟล์รูปได้")

    results = model.predict(frame, conf=confidence, verbose=False)
    result = results[0]

    detections = []
    for box in result.boxes:
        detections.append({
            "class": int(box.cls),
            "class_name": result.names[int(box.cls)],
            "confidence": round(float(box.conf), 4),
            "bbox": box.xyxy.tolist()[0],
        })

    annotated = result.plot()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"detect_{timestamp}.jpg"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    cv2.imwrite(output_path, annotated)

    return {
        "fish_count": len(detections),
        "detections": detections,
        "result_image": f"/results/{output_filename}"
    }


@app.get("/results/{filename}")
def get_result_image(filename: str):
    """ดึงรูป/วิดีโอผลลัพธ์การตรวจจับ"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์")
    if filename.endswith('.mp4'):
        return FileResponse(filepath, media_type="video/mp4")
    return FileResponse(filepath, media_type="image/jpeg")


@app.post("/detect/video")
async def detect_video(
    file: UploadFile = File(...),
    confidence: float = 0.25
):
    """
    อัปโหลดวิดีโอ → AI ตรวจจับปลาทีละ frame → return วิดีโอผลลัพธ์

    - **file**: ไฟล์วิดีโอ (mp4, avi, mov)
    - **confidence**: ค่า confidence threshold (default: 0.25)
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model ยังไม่ได้โหลด")

    # บันทึกวิดีโอชั่วคราว
    tmp_dir = tempfile.mkdtemp()
    tmp_input = os.path.join(tmp_dir, 'input_video' + os.path.splitext(file.filename or '.mp4')[1])
    try:
        with open(tmp_input, 'wb') as f:
            content = await file.read()
            f.write(content)

        cap = cv2.VideoCapture(tmp_input)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="ไม่สามารถเปิดไฟล์วิดีโอได้")

        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


        # เตรียมไฟล์ output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"video_{timestamp}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0
        frames_with_fish = 0
        import time
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            results = model.predict(frame, conf=confidence, verbose=False)
            result = results[0]

            if len(result.boxes) > 0:
                frames_with_fish += 1

            annotated_frame = result.plot()
            writer.write(annotated_frame)

        cap.release()
        writer.release()

        # แปลง mp4v → H.264 เพื่อให้ browser เล่นได้
        h264_filename = f"video_{timestamp}_h264.mp4"
        h264_path = os.path.join(OUTPUT_DIR, h264_filename)
        if convert_to_h264(output_path, h264_path):
            os.remove(output_path)  # ลบไฟล์ mp4v เดิม
            final_filename = h264_filename
        else:
            final_filename = output_filename

        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        processing_time = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"

        return {
            "total_frames": total_frames,
            "frames_with_fish": frames_with_fish,
            "processing_time": processing_time,
            "result_video": f"/results/{final_filename}"
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
