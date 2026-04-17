# python:3.11-slim รองรับทั้ง x86_64 และ ARM64 (Raspberry Pi 5)
# เบากว่า pytorch/pytorch (~120MB vs ~5GB) เพราะ backend ไม่ได้รัน YOLO
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# สร้าง User ใหม่ชื่อ 'appuser' (UID 1000) เพื่อความปลอดภัย
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/sh -m appuser

# ตั้ง Folder ทำงานเป็น /code
WORKDIR /code

# psycopg2-binary ต้องการ libpq เท่านั้น
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt และ Install
# [NOTE] เรา Copy แค่ไฟล์นี้ก่อน เพื่อให้ Docker Cache layer นี้ไว้ได้ถ้า code เปลี่ยนแต่ lib ไม่เปลี่ยน
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy Code ทั้งหมดเข้าไป
COPY . .

# [NEW] เปลี่ยนเจ้าของไฟล์ทั้งหมดให้เป็น appuser
# เพื่อให้ User ใหม่มีสิทธิ์อ่าน/เขียนไฟล์ใน /code ได้ (เช่นสร้างไฟล์ temp หรือ log)
RUN chown -R appuser:appuser /code

# [NEW] สลับมาใช้ User 'appuser' ในการรัน Service
USER appuser

# เปิด Port 8000
EXPOSE 8000

# [NEW] ปรับ CMD ให้รองรับ Production และ Cloud Tunnel
# 1. --host 0.0.0.0: เพื่อให้ฟัง request จากภายนอก container
# 2. --proxy-headers: [สำคัญมากสำหรับ Cloud Tunnel/Nginx]
#    เพื่อให้ FastAPI รู้ว่า Client IP จริงๆ คืออะไร (ไม่ใช่ 127.0.0.1 จาก Tunnel)
#    และรู้ว่า Client เข้ามาด้วย https หรือ http
# 3. --forwarded-allow-ips "*": อนุญาตให้รับ Header จาก Tunnel IP ใดๆ ก็ได้ (เพราะ Cloudflare IP เปลี่ยนไปมา)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]