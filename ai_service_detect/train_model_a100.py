from ultralytics import YOLO
import os
import shutil
import yaml
import glob
import pathlib

# --- 1. Settings ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(CURRENT_DIR, 'datasets')
DATA_YAML_PATH = os.path.join(DATASET_DIR, 'data.yaml')

# Destination for the best model (where the team will pick it up)
DEST_MODEL_DIR = os.path.join(CURRENT_DIR, 'models')
DEST_MODEL_PATH = os.path.join(DEST_MODEL_DIR, 'best_yolov8n_a100.pt')

def force_fix_yaml():
    """Ensure data.yaml uses absolute paths and correct classes."""
    print(f"🔧 Checking and fixing data.yaml...")
    if not os.path.exists(DATA_YAML_PATH):
        print(f"❌ File not found: {DATA_YAML_PATH}")
        print(f"   Please upload your dataset to: {DATASET_DIR}")
        return False

    with open(DATA_YAML_PATH, 'r', encoding='utf-8') as f:
        try:
            old_data = yaml.safe_load(f)
        except yaml.YAMLError:
            old_data = {}

    if os.path.exists(os.path.join(DATASET_DIR, 'valid')):
        val_dir_name = 'valid'
    else:
        val_dir_name = 'val'
    
    # Enforce absolute paths
    new_data = {
        'path': DATASET_DIR,
        'train': os.path.join(DATASET_DIR, 'train', 'images'),
        'val': os.path.join(DATASET_DIR, val_dir_name, 'images'),
        'test': os.path.join(DATASET_DIR, 'test', 'images'),
    }

    # Preserve or set default names
    if old_data and 'names' in old_data:
        new_data['names'] = old_data['names']
        print(f"✅ Found classes: {new_data['names']}")
    else:
        # Default fallback if no names found (User should check this!)
        new_data['names'] = {0: 'Tilapia', 1: 'Goldfish'} # Example defaults
        print(f"⚠️ Warning: No class names found in old yaml. Using defaults: {new_data['names']}")
    
    # Preserve nc (number of classes) if exists, else infer
    if old_data and 'nc' in old_data:
        new_data['nc'] = old_data['nc']
    else:
        new_data['nc'] = len(new_data['names'])

    with open(DATA_YAML_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(new_data, f, default_flow_style=False, allow_unicode=True)

    print(f"✅ Config check passed!")
    return True

def find_latest_best_model():
    """Finds the 'freshest' best.pt in the runs directory."""
    search_dir = os.path.join(CURRENT_DIR, 'runs')
    best_file = None
    latest_time = 0

    print(f"🔍 Scanning for latest best.pt in {search_dir} ...")
    
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file == 'best.pt':
                full_path = os.path.join(root, file)
                # Check file modification time
                file_time = os.path.getmtime(full_path)
                if file_time > latest_time:
                    latest_time = file_time
                    best_file = full_path

    return best_file

def main():
    # 1. Fix Config
    if not force_fix_yaml():
        return

    print("🚀 Starting YOLOv8n Training on A100...")

    # 2. Start Training
    # Load a pretrained YOLOv8n model
    model = YOLO('yolov8n.pt') 
    
    try:
        results = model.train(
            data=DATA_YAML_PATH,
            epochs=300,             # Long training for max accuracy
            imgsz=640,              # Standard size, could go 1280 if needed but 640 is good for RPi
            batch=256,              # High batch size for A100 80GB
            device=0,               # Use first GPU
            project='runs/detect',
            name='yolov8n_fish_a100',
            patience=50,            # Early stopping
            workers=16,             # 16 CPU threads for data loading
            exist_ok=True,          # Overwrite existing experiment name
            cache=True,             # Cache images in RAM for speed
            optimizer='SGD',        # SGD often generalizes better than Adam for YOLO
            cos_lr=True,            # Cosine learning rate scheduler
            warmup_epochs=5,        # Warmup
            close_mosaic=10,        # Disable mosaic augmentation for last 10 epochs
        )
    except Exception as e:
        print(f"⚠️ Error during training: {e}")

    # 3. Smart Copy
    print("\n" + "="*50)
    print("📦 Auto-Archiving Best Model...")

    latest_model = find_latest_best_model()

    if latest_model:
        print(f"✅ Found best model at: {latest_model}")
        
        os.makedirs(DEST_MODEL_DIR, exist_ok=True)
        
        try:
            shutil.copy(latest_model, DEST_MODEL_PATH)
            print(f"🎉 Success! The model is ready at: {DEST_MODEL_PATH}")
            print(f"👉 You can download this file to your Raspberry Pi.")
        except Exception as e:
            print(f"❌ Copy failed: {e}")
    else:
        print(f"❌ No best.pt found. Did training start?")
    
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
