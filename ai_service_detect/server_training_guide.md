# 🎣 Fish Detection Training Guide (A100 Server)

This guide will walk you through training a **YOLOv8n** model on the high-performance **A100** server. This model is optimized for deployment on **Raspberry Pi 5**.

---

## 🚀 1. Preparing Your Dataset

Before jumping onto the server, you need to prepare your images.

1.  **Collect Images**: Gather images of **Tilapia**, **Goldfish**, and other fish you want to detect.
2.  **Label Images**: Use [Roboflow](https://roboflow.com/) or [LabelImg](https://github.com/HumanSignal/labelImg) to draw bounding boxes around the fish.
    - **Class 0**: Tilapia
    - **Class 1**: Goldfish
    - _(Add more classes as needed)_
3.  **Export Dataset**: Export as **YOLOv8** format. You should get a folder structure like this:
    ```
    dataset/
      ├── data.yaml
      ├── train/
      │   ├── images/
      │   └── labels/
      └── valid/ (or val/)
          ├── images/
          └── labels/
    ```

---

## 📤 2. Uploading to Server

You need to get your dataset onto the `br1` login node.

**Option A: Using SCP (Command Line)**
Run this from your _local computer_ (not the server):

```bash
scp -r /path/to/your/dataset aip09@br1.paas.ku.ac.th:~/proj/underwater-project-v1/ai_service_detect/datasets/
```

**Option B: Using Git**
If your dataset is small (<100MB), you can commit it to Git. If it's large, use SCP or Google Drive (wget).

---

## 🖥️ 3. Login to Server

Login to the head node:

```bash
ssh aip09@br1.paas.ku.ac.th
# Enter password
```

Navigate to the project folder:

```bash
cd ~/proj/underwater-project-v1/ai_service_detect
```

---

## ⚡ 4. Start Training (The Fun Part)

Since the login node (`br1`) doesn't have a GPU, we must submit a job to the compute node (`gpuq`) which has the **A100**.

We have prepared a script `submit_job.sh` for you.

### Step 4.1: Submit the Job

Run this command:

```bash
sbatch submit_job.sh
```

### Step 4.2: Monitor Progress

Check if your job is in the queue or running:

```bash
squeue -u aip09
```

- **ST (Status)**: `PD` = Pending (Waiting for GPU), `R` = Running.

### Step 4.3: Watch the Logs

To see the training output in real-time (loss, epochs, etc.):

```bash
tail -f slurm-*.out
```

_(Press `Ctrl+C` to stop watching. The training continues in the background.)_

---

## 📦 5. Get Your Model

The training script is smart. It will automatically copy the best model to the `models/` folder once done.

**Location on Server:**
`~/proj/underwater-project-v1/ai_service_detect/models/best_yolov8n_a100.pt`

**Download to Your Computer:**
Run this on your _local computer_:

```bash
scp aip09@br1.paas.ku.ac.th:~/proj/underwater-project-v1/ai_service_detect/models/best_yolov8n_a100.pt ./
```

Now you can transfer this `.pt` file to your **Raspberry Pi 5** and run it!

---

## 🛠️ Advanced: Customize Training

If you want to change parameters (like epochs), edit `train_model_a100.py`:

```python
# train_model_a100.py

epochs=300       # Increase for better accuracy (if you have time)
batch=256        # A100 has 80GB VRAM, so we can use a huge batch size!
```

---

### ❓ Troubleshooting

- **`sbatch: command not found`**: Ensure you are on `br1` login node and have the cluster module loaded (usually automatic).
- **`CUDA not available`**: Make sure `submit_job.sh` has `#SBATCH --gres=gpu:1`.
