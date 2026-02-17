#!/bin/bash
#SBATCH --job-name=setup_env
#SBATCH --output=setup_env.out
#SBATCH --error=setup_env.err
#SBATCH --partition=gpuq
#SBATCH --nodes=1
#SBATCH --gres=gpu:1

# Load modules
echo "📦 Loading modules..."
module load cuda/12.1

# Activate Conda
echo "🐍 Activating Conda environment..."
source ~/.bashrc

# Create Environment if not exists
if ! conda info --envs | grep -q "yolo_env"; then
    echo "Creating environment 'yolo_env'..."
    conda create -n yolo_env python=3.10 -y
fi

source activate yolo_env

# Install Libraries
echo "📦 Installing libraries..."
pip install ultralytics
pip install opencv-python-headless
pip install PyYAML

echo "✅ Setup Complete!"
