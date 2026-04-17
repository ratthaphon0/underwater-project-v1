import random
import os
try:
    import joblib
except ImportError:
    joblib = None

class ModelEngine:
    def __init__(self):
        # ---------------------------------------------------------
        # 📌 สำหรับทีม DataSci: 
        # วิธีนำ Model มาฝัง: เอาไฟล์ .pkl มาวางไว้ใน backend/models/
        # แล้วเปลี่ยนชื่อ MODEL_PATH ด้านล่างให้ตรงกัน
        # ---------------------------------------------------------
        self.MODEL_PATH = "models/water_quality_model.pkl"
        
        if joblib and os.path.exists(self.MODEL_PATH):
            print(f"✅ Loading real ML model from {self.MODEL_PATH}")
            self.model = joblib.load(self.MODEL_PATH)
            self.model_version = "prod-v1.0"
        else:
            print(f"⚠️ Warning: Model file {self.MODEL_PATH} not found or joblib not installed. Using Mockup Model.")
            self.model = None
            self.model_version = "mock-v1.0"

    def predict_water_quality(self, data: dict):
        """
        Inference System for Data Science Model.
        Input: Dictionary of sensor data (temp, ph, etc.)
        Output: Dictionary of predicted values for next hour
        """
        current_do = data.get("do_level", 5.0)
        current_ph = data.get("ph", 7.0)
        
        # 1. 🟢 ทำงานด้วย Model จริง (ถ้าโหลดสำเร็จ)
        if self.model:
            try:
                # ปรับโครงสร้าง Feature ให้ตรงกับที่ DataSci เทรนมา
                # เช่น X_test = [[temp, ph, turbidity, ...]]
                features = [[
                    data.get("temp", 25.0),
                    data.get("ph", 7.0),
                    data.get("turbidity", 10.0)
                ]]
                # สมมติโมเดลคืนค่า 2 อย่างคือ [predicted_do, predicted_ph]
                prediction = self.model.predict(features)[0] 
                
                return {
                    "DO": {
                        "predicted_value": round(prediction[0], 2),
                        "confidence_interval": 0.95, # โมเดลบางตัวอาจจะมี predict_proba
                    },
                    "pH": {
                        "predicted_value": round(prediction[1], 2),
                        "confidence_interval": 0.90,
                    }
                }
            except Exception as e:
                print(f"❌ ML Prediction Error: {e}")
                # Fallback to mock

        # 2. 🟡 ทำงานด้วย Mockup (ใช้ในตอนทดสอบหรือยังไม่มีไฟล์โมเดล)
        return {
            "DO": {
                "predicted_value": round(current_do * random.uniform(0.95, 1.05), 2),
                "confidence_interval": round(random.uniform(0.8, 0.99), 2),
            },
            "pH": {
                "predicted_value": round(current_ph * random.uniform(0.98, 1.02), 2),
                "confidence_interval": round(random.uniform(0.8, 0.99), 2),
            }
        }

model_engine = ModelEngine()
