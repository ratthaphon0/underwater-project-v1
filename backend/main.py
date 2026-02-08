from fastapi import FastAPI
import torch

app = FastAPI()

@app.get("/")
def read_root():
    gpu_status = torch.cuda.is_available()
    return {
        "message": "Underwater AI Backend is Running!",
        "gpu_available": gpu_status,
        "gpu_name": torch.cuda.get_device_name(0) if gpu_status else "CPU"
    }