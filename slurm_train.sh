#!/bin/bash
#SBATCH -p gpuq
#SBATCH -A gm_aip18
#SBATCH --gres=gpu:1g.10gb:1
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --job-name=yolo_S_Simple_NoConda
#SBATCH --output=log_Simple_%j.out
#SBATCH --error=log_Simple_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ratthaphon.kha@ku.th

# ==========================================
# 🔧 รันตรงๆ จากที่เดิม (ไม่ย้ายไป Scratch แล้ว)
# ==========================================
export WORK_DIR=$SLURM_SUBMIT_DIR
cd $WORK_DIR

echo "=========================================="
echo "Work Dir: $WORK_DIR"
echo "Dataset Check:"
ls -l dataset/data.yaml
echo "=========================================="

# Load Module (เอาแค่ Python พื้นฐาน)
module load miniconda3

# ❌ ไม่ต้อง Activate Conda (เพราะสร้างไม่ได้)
# source activate yolov8  <-- ปิดไว้

echo "=========================================="
echo "Checking Environment..."
echo "Python Path: $(which python)"
python --version
# เช็ค package ว่าเจอไหม (ของ user local)
pip show ultralytics || echo "⚠️ Warning: ultralytics not found via pip show"
echo "=========================================="

# รันเลย (Batch Size 16)
echo "⚡ Starting YOLOv8 Training (yolov8n.pt)..."
python train_nontri.py "$WORK_DIR/dataset"
