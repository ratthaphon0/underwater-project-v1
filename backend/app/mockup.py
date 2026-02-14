import psycopg2
import uuid
import time
import random
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# ==========================================
# 0. Load Environment Variables (.env)
# ==========================================
current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    load_dotenv()
    print("⚠️  .env not found in parent dir, trying current dir...")

# ==========================================
# 1. การตั้งค่า Database
# ==========================================
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "underwater_db"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "supaporn2026"),
    "host": "localhost",
    "port": os.getenv("DB_PORT", "5433") # ตรวจสอบ Port ให้ตรง (5432 หรือ 5433)
}

print("⚙️  DB Config:", DB_CONFIG)

# จำลองพิกัดเริ่มต้น
START_LAT = 13.7563
START_LNG = 100.5018

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

# ==========================================
# 2. ฟังก์ชันหลัก (ปรับให้ตรงกับ init.sql)
# ==========================================

def start_session(cursor, location, notes):
    """สร้าง Session การเดินเรือใหม่"""
    # ใน init.sql ใช้ id UUID PRIMARY KEY
    session_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    # ตัด weather_type, activity_type ออก เพราะไม่มีใน Schema
    sql = """
        INSERT INTO public.monitoring_sessions 
        (id, start_time, location_name, notes)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (session_id, start_time, location, notes))
    print(f"✅ [Session Started] ID: {session_id}")
    return session_id

def insert_telemetry(cursor, session_id, current_time):
    """จำลองข้อมูล Sensor (แก้ชื่อ Column ให้ตรง init.sql)"""
    
    lat = START_LAT + random.uniform(-0.0005, 0.0005)
    lng = START_LNG + random.uniform(-0.0005, 0.0005)
    depth = round(random.uniform(1.5, 3.0), 2)
    
    # ชื่อตัวแปรตรงกับ init.sql
    temperature = round(random.uniform(26.0, 29.5), 2)
    ph = round(random.uniform(7.0, 8.2), 2)
    dissolved_oxygen = round(random.uniform(4.5, 6.0), 2) # เปลี่ยนจาก do_level
    ec_tds = round(random.uniform(0.4, 0.6), 2)           # เปลี่ยนจาก ec_value
    turbidity = round(random.uniform(10.0, 50.0), 2)
    
    sql = """
        INSERT INTO public.water_telemetry 
        (session_id, timestamp, lat, lng, depth, temperature, ph, dissolved_oxygen, ec_tds, turbidity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        session_id, current_time, lat, lng, depth, 
        temperature, ph, dissolved_oxygen, ec_tds, turbidity
    ))
    print(f"   📊 [Telemetry] Temp: {temperature}C | DO: {dissolved_oxygen} | TDS: {ec_tds}")

def insert_fish_detection(cursor, session_id, current_time):
    """จำลอง AI Vision"""
    
    fish_count = random.randint(1, 15)
    health_status = random.choice(['Healthy', 'Suspicious', 'Critical'])
    
    metadata = {
        "confidence": round(random.uniform(0.85, 0.99), 2),
        "species": "Nile Tilapia"
    }
    
    sql = """
        INSERT INTO public.fish_detections 
        (session_id, timestamp, raw_image_path, enhanced_image_path, fish_count, detection_metadata, health_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    raw_path = f"/data/images/{session_id}/raw_{int(current_time.timestamp())}.jpg"
    enh_path = f"/data/images/{session_id}/enh_{int(current_time.timestamp())}.jpg"

    cursor.execute(sql, (
        session_id, current_time, raw_path, enh_path, 
        fish_count, json.dumps(metadata), health_status
    ))
    print(f"   🐟 [Fish Found] Count: {fish_count} | Status: {health_status}")

def insert_prediction(cursor, session_id, current_time):
    """จำลองตาราง Prediction (Table 4)"""
    # ทำนายค่า DO ในอีก 1 ชั่วโมงข้างหน้า
    predicted_val = round(random.uniform(4.0, 5.5), 2)
    predict_time = current_time + timedelta(hours=1)
    
    sql = """
        INSERT INTO public.water_predictions
        (session_id, base_timestamp, predict_for_timestamp, parameter_name, predicted_value, confidence_interval, model_version)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        session_id, current_time, predict_time, 
        "dissolved_oxygen", predicted_val, 0.95, "v1.0.0"
    ))
    print(f"   🔮 [Prediction] Forecast DO: {predicted_val} @ {predict_time.strftime('%H:%M')}")

def end_session(cursor, session_id):
    """ปิด Job"""
    end_time = datetime.now()
    
    sql = """
        UPDATE public.monitoring_sessions 
        SET end_time = %s 
        WHERE id = %s
    """
    cursor.execute(sql, (end_time, session_id))
    print(f"🛑 [Session Ended] at {end_time}")

# ==========================================
# 3. Main Simulation Loop
# ==========================================
def run_simulation():
    conn = get_db_connection()
    if not conn:
        print("❌ Cannot connect to DB.")
        return

    try:
        cursor = conn.cursor()
        
        # 1. เริ่มภารกิจ (Start Session)
        session_uuid = start_session(cursor, "Zone A - North Pond", "Water looks clear today.")
        conn.commit()

        # 2. จำลองการวิ่งเรือ 10 วินาที
        for i in range(1, 11):
            current_timestamp = datetime.now()
            
            # 2.1 เก็บค่า Sensor (Telemetry)
            insert_telemetry(cursor, session_uuid, current_timestamp)
            
            # 2.2 สุ่มเจอ ปลา (30%)
            if random.random() < 0.3:
                insert_fish_detection(cursor, session_uuid, current_timestamp)
            
            # 2.3 สุ่มทำนายค่า (20%)
            if random.random() < 0.2:
                insert_prediction(cursor, session_uuid, current_timestamp)
            
            time.sleep(1) 
            
        conn.commit() # Save ระหว่างทาง

        # 3. จบภารกิจ
        end_session(cursor, session_uuid)
        conn.commit()

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("--- Connection Closed ---")

if __name__ == "__main__":
    run_simulation()