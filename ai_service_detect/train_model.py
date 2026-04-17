"""
train_model.py — เทรนโมเดล YOLOv8 สำหรับตรวจจับปลานิล

วิธีใช้:
    python train_model.py

ผลลัพธ์:
    models/best.pt  ← โมเดลที่ดีที่สุด พร้อมใช้งานโดย app.py และ ai_tracker.py
"""

from ultralytics import YOLO
import os
import shutil
import yaml

# ─── Paths ────────────────────────────────────────────────────────────────────

CURRENT_DIR    = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR    = os.path.join(CURRENT_DIR, "datasets")
DATA_YAML_PATH = os.path.join(DATASET_DIR, "data.yaml")
DEST_MODEL_DIR = os.path.join(CURRENT_DIR, "models")
DEST_MODEL_PATH = os.path.join(DEST_MODEL_DIR, "best.pt")


# ─── Fix data.yaml ────────────────────────────────────────────────────────────

def force_fix_yaml() -> bool:
    """
    เขียน data.yaml ใหม่ด้วย absolute path ที่ถูกต้อง
    แก้ปัญหา path สะกดผิด หรือ path เก่าที่ hardcode ไว้ผิด
    """
    print("Checking data.yaml...")

    if not os.path.exists(DATASET_DIR):
        print(f"[Error] Dataset dir not found: {DATASET_DIR}")
        return False

    # รองรับทั้ง valid/ และ val/
    val_dir = "valid" if os.path.exists(os.path.join(DATASET_DIR, "valid")) else "val"

    # อ่าน names/nc จาก yaml เดิมถ้ามี
    names = {0: "Tilapia"}
    nc    = 1
    if os.path.exists(DATA_YAML_PATH):
        with open(DATA_YAML_PATH, "r", encoding="utf-8") as f:
            try:
                old = yaml.safe_load(f) or {}
                if "names" in old:
                    names = old["names"]
                if "nc" in old:
                    nc = old["nc"]
            except yaml.YAMLError:
                pass

    new_data = {
        "path":  DATASET_DIR,
        "train": os.path.join(DATASET_DIR, "train", "images"),
        "val":   os.path.join(DATASET_DIR, val_dir, "images"),
        "test":  os.path.join(DATASET_DIR, "test", "images"),
        "nc":    nc,
        "names": names,
    }

    with open(DATA_YAML_PATH, "w", encoding="utf-8") as f:
        yaml.dump(new_data, f, default_flow_style=False, allow_unicode=True)

    print(f"  data.yaml updated: {DATA_YAML_PATH}")
    print(f"  train : {new_data['train']}")
    print(f"  val   : {new_data['val']}")
    print(f"  classes: {names}")
    return True


# ─── Find Best Model ──────────────────────────────────────────────────────────

def find_latest_best_model() -> str | None:
    """ค้นหา best.pt ที่ใหม่ที่สุดในโฟลเดอร์ runs/"""
    search_dir  = os.path.join(CURRENT_DIR, "runs")
    best_file   = None
    latest_time = 0

    print(f"Scanning for best.pt in {search_dir} ...")
    for root, _, files in os.walk(search_dir):
        for f in files:
            if f == "best.pt":
                full  = os.path.join(root, f)
                mtime = os.path.getmtime(full)
                if mtime > latest_time:
                    latest_time = mtime
                    best_file   = full

    return best_file


# ─── Count Dataset ────────────────────────────────────────────────────────────

def count_dataset() -> dict:
    splits = {}
    for split in ("train", "valid", "val", "test"):
        img_dir = os.path.join(DATASET_DIR, split, "images")
        if os.path.exists(img_dir):
            exts  = (".jpg", ".jpeg", ".png")
            count = sum(1 for f in os.listdir(img_dir) if f.lower().endswith(exts))
            splits[split] = count
    return splits


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    # 1. ตรวจสอบ dataset
    counts = count_dataset()
    print("\nDataset summary:")
    for split, n in counts.items():
        print(f"  {split:8s}: {n} images")

    train_count = counts.get("train", 0)
    if train_count < 50:
        print(f"\n[Warning] Only {train_count} training images.")
        print("  Run extract_frames.py and label images first for better results.")

    # 2. Fix data.yaml
    if not force_fix_yaml():
        return

    # 3. เลือก base model
    #    YOLOv8s ดีกว่า YOLOv8n ~5-8% mAP บน dataset เล็ก
    #    ดาวน์โหลดอัตโนมัติถ้ายังไม่มีไฟล์
    BASE_MODEL = "yolov8s.pt"
    print(f"\nBase model: {BASE_MODEL}")
    print("Starting training...")

    model = YOLO(BASE_MODEL)

    try:
        model.train(
            data=DATA_YAML_PATH,

            # ─── Training schedule ────────────────────────────────────
            epochs=100,           # เพิ่มจาก 50 เป็น 100 (dataset เล็ก ต้องเทรนนานขึ้น)
            patience=20,          # early stop ถ้า val loss ไม่ดีขึ้น 20 epochs
            imgsz=640,
            batch=16,             # เพิ่มจาก 8 เป็น 16 (ถ้า GPU RAM ไม่พอ จะ fallback อัตโนมัติ)

            # ─── Hardware ────────────────────────────────────────────
            device=0,             # GPU 0 — เปลี่ยนเป็น "cpu" ถ้าไม่มี GPU
            workers=2,

            # ─── Underwater augmentation ─────────────────────────────
            # สีน้ำเปลี่ยนตามความลึก/แสง — สำคัญมากสำหรับ underwater footage
            hsv_h=0.02,           # hue ±2%   (สีน้ำแตกต่างกัน)
            hsv_s=0.7,            # saturation ±70%
            hsv_v=0.5,            # brightness ±50% (แสงใต้น้ำแปรปรวน)
            # ─── Geometric ───────────────────────────────────────────
            fliplr=0.5,           # พลิกซ้าย-ขวา (ปลาว่ายสองทิศ)
            flipud=0.1,           # พลิกแนวตั้งเบาๆ
            degrees=5.0,          # หมุน ±5° (กล้องใต้น้ำเอียงได้)
            translate=0.1,        # เลื่อนภาพ ±10%
            scale=0.5,            # zoom in/out ±50%
            # ─── Advanced ────────────────────────────────────────────
            mosaic=1.0,           # รวม 4 ภาพ = เหมือนมี dataset 4 เท่า
            mixup=0.1,            # blend 2 ภาพ เพิ่ม generalization
            copy_paste=0.1,       # cut-paste ปลาจากภาพหนึ่งไปอีกภาพ

            # ─── Output ──────────────────────────────────────────────
            project="runs/detect",
            name="tilapia_v2",
            exist_ok=True,
            save_period=10,       # checkpoint ทุก 10 epochs
        )
    except Exception as e:
        print(f"[Warning] Training error (may still have best.pt): {e}")

    # 4. Copy best.pt ไปที่ models/
    print("\n" + "=" * 50)
    print("Copying best model...")

    latest = find_latest_best_model()
    if latest:
        os.makedirs(DEST_MODEL_DIR, exist_ok=True)
        try:
            shutil.copy(latest, DEST_MODEL_PATH)
            size_mb = os.path.getsize(DEST_MODEL_PATH) / 1024 / 1024
            print(f"  Source : {latest}")
            print(f"  Dest   : {DEST_MODEL_PATH} ({size_mb:.1f} MB)")
            print(f"\nModel ready: {DEST_MODEL_PATH}")
        except Exception as e:
            print(f"[Error] Copy failed: {e}")
    else:
        print("[Error] No best.pt found in runs/")

    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
