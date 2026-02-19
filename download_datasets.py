import os
import shutil
from roboflow import Roboflow

# --- Configuration ---
API_KEY = "JIoN8mhhn42e6QajOWDS" 
# WORKSPACE_PROJECTS = [] # Done downloading

DATASET_ROOT = "dataset_nontri"
FINAL_DATASET_DIR = "dataset"
LOCAL_TILAPIA_DIR = "ai_service_detect/datasets"

def merge_local_tilapia():
    print(f"\n🐟 Merging LOCAL Tilapia dataset from '{LOCAL_TILAPIA_DIR}'...")
    
    if not os.path.exists(LOCAL_TILAPIA_DIR):
        print(f"⚠️ Local Tilapia dir '{LOCAL_TILAPIA_DIR}' not found!")
        return

    # Mappings: local dir name -> final dir name
    # local: train, valid, test
    # final: train, valid, test
    
    for split in ['train', 'valid', 'test']:
        # Handle 'val' vs 'valid' naming in local
        local_split = split
        if split == 'valid' and not os.path.exists(os.path.join(LOCAL_TILAPIA_DIR, split)):
            if os.path.exists(os.path.join(LOCAL_TILAPIA_DIR, 'val')):
                local_split = 'val'
        
        src_dir = os.path.join(LOCAL_TILAPIA_DIR, local_split)
        
        if not os.path.exists(src_dir):
            continue
            
        # Images and Labels usually in 'images' and 'labels' subdirs?
        # Let's check if 'images' subdir exists, or if images are directly in split dir
        # Based on typical YOLO structure: split/images and split/labels
        
        src_images = os.path.join(src_dir, 'images')
        src_labels = os.path.join(src_dir, 'labels')
        
        # Fallback if no 'images' subdir (flat structure)
        if not os.path.exists(src_images):
            # Assume flat structure, copy from src_dir directly
            src_images = src_dir
            src_labels = src_dir # labels mixed with images?
            
        dst_images = os.path.join(FINAL_DATASET_DIR, split, 'images')
        dst_labels = os.path.join(FINAL_DATASET_DIR, split, 'labels')
        
        copied_count = 0
        for file in os.listdir(src_images):
            if file.endswith(('.jpg', '.jpeg', '.png')):
                # Copy Image
                shutil.copy2(os.path.join(src_images, file), os.path.join(dst_images, file))
                
                # Copy Label
                lbl_file = file.rsplit('.', 1)[0] + '.txt'
                src_lbl_path = os.path.join(src_labels, lbl_file)
                dst_lbl_path = os.path.join(dst_labels, lbl_file)
                
                if os.path.exists(src_lbl_path):
                    # Relabel to Class 0 (Tilapia)
                    with open(src_lbl_path, 'r') as f:
                        lines = f.readlines()
                    with open(dst_lbl_path, 'w') as f:
                        for line in lines:
                            parts = line.strip().split()
                            if parts:
                                parts[0] = "0" # Force Class 0
                                f.write(" ".join(parts) + "\n")
                
                copied_count += 1
        print(f"   - Copied {copied_count} images to {split}")

def create_structure():
    print(f"\n🔨 Creating folder structure in '{FINAL_DATASET_DIR}'...")
    for split in ['train', 'valid', 'test']:
        os.makedirs(os.path.join(FINAL_DATASET_DIR, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(FINAL_DATASET_DIR, split, 'labels'), exist_ok=True)

def merge_datasets():
    if not os.path.exists(DATASET_ROOT):
        print(f"⚠️  Folder '{DATASET_ROOT}' not found. Nothing to merge.")
        return

    print(f"\n🔄 Merging datasets from '{DATASET_ROOT}'...")
    
    # Walk through downloaded datasets
    for root, dirs, files in os.walk(DATASET_ROOT):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png')):
                # Determine split
                split = 'train'
                if 'valid' in root or 'val' in root:
                    split = 'valid'
                elif 'test' in root:
                    split = 'test'
                
                # Paths
                src_img = os.path.join(root, file)
                src_lbl = os.path.join(root, file.rsplit('.', 1)[0] + '.txt')
                
                # Copy Image
                dst_img = os.path.join(FINAL_DATASET_DIR, split, 'images', file)
                
                # Avoid overwriting if same filename exists from different dataset
                # Add prefix based on parent folder if needed, but simple copy for now
                if os.path.exists(dst_img):
                    base, ext = os.path.splitext(file)
                    dst_img = os.path.join(FINAL_DATASET_DIR, split, 'images', f"{base}_copy{ext}")

                dst_lbl = os.path.join(FINAL_DATASET_DIR, split, 'labels', os.path.basename(dst_img).rsplit('.', 1)[0] + '.txt')
                
                shutil.copy2(src_img, dst_img)
                
                # Relabel logic (0=Tilapia, 1=Goldfish)
                new_class_id = 0 # Default: Tilapia
                
                # Heuristic: Check path for 'gold' to identify Goldfish
                if "gold" in root.lower() or "gold" in file.lower():
                    new_class_id = 1
                
                if os.path.exists(src_lbl):
                    with open(src_lbl, 'r') as f:
                        lines = f.readlines()
                    with open(dst_lbl, 'w') as f:
                        for line in lines:
                            parts = line.strip().split()
                            if parts:
                                # Overwrite class ID
                                parts[0] = str(new_class_id)
                                f.write(" ".join(parts) + "\n")

    print("✅ Merge complete!")
    create_yaml()

def create_yaml():
    yaml_content = f"""
path: ./dataset
train: train/images
val: valid/images
test: test/images

nc: 2
names: ['Tilapia', 'Goldfish']
"""
    with open(os.path.join(FINAL_DATASET_DIR, 'data.yaml'), 'w') as f:
        f.write(yaml_content.strip())
    print("✅ Created data.yaml")

def download_datasets():
    print(f"🚀 Downloading datasets to '{DATASET_ROOT}'...")
    
    rf = Roboflow(api_key=API_KEY)
    
    # Clean up previous download
    if os.path.exists(DATASET_ROOT):
        shutil.rmtree(DATASET_ROOT)
    os.makedirs(DATASET_ROOT)

    success_count = 0
    for workspace, project_name, version in WORKSPACE_PROJECTS:
        try:
            print(f"\n📥 Downloading {project_name} (v{version})...")
            project = rf.workspace(workspace).project(project_name)
            # Download to specific folder inside root
            dataset = project.version(version).download("yolov8", location=os.path.join(DATASET_ROOT, project_name))
            print(f"✅ Downloaded {project_name}")
            success_count += 1
            
        except Exception as e:
            print(f"⚠️ Failed to download {project_name}: {e}")
            # Continue to next dataset

    print(f"\n✅ Finished. Successful downloads: {success_count}/{len(WORKSPACE_PROJECTS)}")

if __name__ == "__main__":
    create_structure()
    # download_datasets() # Done
    # merge_datasets()    # Done
    merge_local_tilapia() # New: Merge local data
