#!/usr/bin/env python3
"""
สคริปต์สร้าง train_bundle.zip สำหรับเทรนบน A100 Nontri AI
โดยจะรวบรวมเฉพาะไฟล์ที่จำเป็นต้องใช้บน cluster
"""

import os
import zipfile
import shutil
from pathlib import Path

def create_train_bundle():
    """สร้าง train_bundle.zip สำหรับการเทรนบน cluster"""
    
    print("🔥 กำลังสร้าง train_bundle.zip สำหรับ A100 training...")
    
    # ไฟล์ที่ต้องการรวมใน bundle
    files_to_include = [
        'train_nontri.py',           # สคริปต์เทรนหลัก
        'slurm_train.sh',            # สคริปต์ส่งงานเข้า cluster (UPDATED)
        'dataset/data.yaml',         # config ข้อมูล
    ]
    
    # โฟลเดอร์ที่ต้องการรวม (ถ้ามี)
    folders_to_include = [
        'dataset',                   # ข้อมูลการเทรน
    ]
    
    # สร้างโฟลเดอร์ชั่วคราว
    temp_dir = 'temp_bundle'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # สร้าง requirements.txt สำหรับ Nontri โดยเฉพาะ
    with open(os.path.join(temp_dir, 'requirements.txt'), 'w') as f:
        f.write("ultralytics\n")
        f.write("torch\n")
        f.write("torchvision\n")
    print("✅ สร้าง requirements.txt (ultralytics)")

    # คัดลอกไฟล์ที่จำเป็น
    for file_path in files_to_include:
        if os.path.exists(file_path):
            dest = os.path.join(temp_dir, os.path.basename(file_path))
            if file_path.endswith('/'):
                shutil.copytree(file_path, dest, dirs_exist_ok=True)
            else:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(file_path, dest)
            print(f"✅ เพิ่ม: {file_path}")
        else:
            print(f"⚠️ ไม่พบ: {file_path}")
    
    # คัดลอกโฟลเดอร์ที่จำเป็น
    for folder_path in folders_to_include:
        if os.path.exists(folder_path):
            dest = os.path.join(temp_dir, folder_path)
            # copytree ใน python 3.8+ รองรับ dirs_exist_ok=True
            shutil.copytree(folder_path, dest, dirs_exist_ok=True)
            print(f"✅ เพิ่มโฟลเดอร์: {folder_path}")
        else:
            print(f"⚠️ ไม่พบโฟลเดอร์: {folder_path}")
    
    # สร้าง README สำหรับ cluster
    readme_content = """# Underwater Fish Detection - A100 Training Bundle

## วิธีใช้งานบน Nontri AI Cluster (แบบละเอียด)

1. อัปโหลด `train_bundle.zip` ขึ้น Cluster
   ```bash
   scp train_bundle.zip aip18@br1.paas.ku.ac.th:/home/aip18/
   ```

2. SSH เข้าไปและแตกไฟล์
   ```bash
   ssh aip18@br1.paas.ku.ac.th
   unzip train_bundle.zip
   cd train_bundle  # (ถ้า unzip สร้าง folder) หรือถ้าแตกออกมาเลยก็ข้าม
   ```

3. Setup Environment (ครั้งแรก)
   ```bash
   module load miniconda3
   conda create -n yolov8 python=3.9 -y
   source activate yolov8
   pip install -r requirements.txt
   ```

4. ส่ง Job เข้า Cluster
   ```bash
   sbatch slurm_train.sh
   ```

5. ดูสถานะ
   ```bash
   squeue -u aip18
   ```

6. ดู Log การทำงาน
   ```bash
   tail -f log_max_*.out
   ```
"""
    
    with open(os.path.join(temp_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # สร้าง zip file
    zip_filename = 'train_bundle.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # ลบโฟลเดอร์ชั่วคราว
    shutil.rmtree(temp_dir)
    
    # แสดงขนาดไฟล์
    file_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
    print(f"\n🎉 สร้าง {zip_filename} เสร็จสิ้น!")
    print(f"📦 ขนาดไฟล์: {file_size:.1f} MB")
    print(f"📋 พร้อมอัปโหลดขึ้น Nontri AI cluster!")

if __name__ == '__main__':
    create_train_bundle()
