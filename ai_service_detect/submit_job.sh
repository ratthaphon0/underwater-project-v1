#!/bin/bash
#SBATCH --job-name=yolo_fish_train
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --partition=gpuq          # Partition provided by user
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:7g.80gb:1      # Request 1 A100 GPU (80GB VRAM)
#SBATCH --cpus-per-task=16        # Request 16 CPU cores
#SBATCH --mem=64G                 # Request 64GB RAM
#SBATCH --time=24:00:00           # Max time 24 hours
#SBATCH --account=gm_aip09        # Account provided by user

# --- 1. Environment Setup ---
echo "========================================"
echo "🚀 Starting Job on Host: $(hostname)"
echo "📅 Date: $(date)"
echo "========================================"

# Load necessary modules (adjust versions if needed based on `module avail`)
echo "📦 Loading modules..."
module load cuda/12.1

# Verify GPU
echo "🔍 Checking GPU..."
nvidia-smi

# Activate Conda Environment
echo "🐍 Activating Conda environment..."
source ~/.bashrc
# Attempt to activate 'deepseek' as user mentioned it works, or fallback to base
if conda info --envs | grep -q "deepseek"; then
    echo "✅ Activating 'deepseek' environment..."
    source activate deepseek
else
    echo "⚠️ 'deepseek' environment not found. Creating a new one 'yolo_env'..."
    conda create -n yolo_env python=3.10 -y
    source activate yolo_env
    pip install ultralytics
fi

# Install dependencies if missing (just in case)
pip install ultralytics

# --- 2. Run Training ---
echo "========================================"
echo "🏋️ Start Training..."
echo "========================================"

# Navigate to script directory
cd $HOME/proj/underwater-project-v1/ai_service_detect

# Run the Python script
python train_model_a100.py

echo "========================================"
echo "✅ Job Completed!"
echo "========================================"
