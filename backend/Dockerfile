# ใช้ Base Image เดิมของคุณ (ดีแล้วสำหรับ AI)
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ตั้ง Folder ทำงานเป็น /code (หรือ /app ก็ได้)
WORKDIR /code

# Install System Dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt จากโฟลเดอร์ backend (ชั้นปัจจุบัน) ไปใส่ใน Image
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ทุกอย่าง (รวมถึงโฟลเดอร์ app/) เข้าไปใน Image
COPY . .

# เปิด Port
EXPOSE 8000

# 🚀 จุดสำคัญที่แก้: เปลี่ยน main:app เป็น "app.main:app"
# เพราะตอนนี้ main.py อยู่ข้างในโฟลเดอร์ app อีกที
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]