FROM python:3.11-slim

# System dependencies
# - libgl1, libglib2.0-0 : OpenCV
# - ffmpeg               : H.264 video conversion
# - v4l-utils, libv4l-dev: Video4Linux — webcam access ใน Linux container
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    v4l-utils \
    libv4l-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

# workers=1 เพราะ YOLO model ใช้ memory เยอะ, timeout=300 สำหรับ video upload ใหญ่
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", \
     "--workers", "1", "--timeout-keep-alive", "300"]
