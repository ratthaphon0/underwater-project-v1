#!/bin/bash

# สคริปต์อัปโหลดไฟล์ขึ้น Nontri AI Cluster
# ปรับให้ใช้งานง่ายขึ้น

echo "🚀 เตรียมอัปโหลดไฟล์ขึ้น Nontri AI Cluster..."

# ตัวแปรคอนฟิก
BUNDLE_FILE="train_bundle.zip"
SLURM_FILE="slurm_train.sh"
REMOTE_USER="aip15"
REMOTE_HOST="login.nontri.ku.ac.th"
REMOTE_DIR="~/yolo_training"

# เช็คว่ามีไฟล์ที่จำเป็นไหม
if [ ! -f "$BUNDLE_FILE" ]; then
    echo "❌ ไม่พบไฟล์ $BUNDLE_FILE กรุณารัน python3 create_train_bundle.py ก่อน"
    exit 1
fi

if [ ! -f "$SLURM_FILE" ]; then
    echo "❌ ไม่พบไฟล์ $SLURM_FILE"
    exit 1
fi

echo "✅ พบไฟล์ที่จำเป็นทั้งหมด"

# สร้างโฟลเดอร์บน remote (ถ้ายังไม่มี)
echo "📁 สร้างโฟลเดอร์ $REMOTE_DIR บน cluster..."
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $REMOTE_DIR"

# อัปโหลดไฟล์
echo "📦 อัปโหลด $BUNDLE_FILE..."
scp "$BUNDLE_FILE" $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/

echo "📄 อัปโหลด $SLURM_FILE..."
scp "$SLURM_FILE" $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/

echo ""
echo "🎉 อัปโหลดเสร็จสิ้น!"
echo ""
echo "📋 ขั้นตอนถัดไปบน cluster:"
echo "1. ssh $REMOTE_USER@$REMOTE_HOST"
echo "2. cd $REMOTE_DIR"
echo "3. unzip train_bundle.zip"
echo "4. แก้ไข USER_DATASET_PATH ใน slurm_train.sh ให้ถูกต้อง"
echo "5. sbatch slurm_train.sh"
echo ""
echo "💡 ตรวจสอบสถานะ: squeue -u $REMOTE_USER"
echo "📋 ดู log: tail -f log_max_*.out"
