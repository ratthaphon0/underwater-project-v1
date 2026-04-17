import logging
import sys

def setup_logging():
    """
    ตั้งค่าระบบ Logging ให้เหมาะสมกับ Production
    - JSON Format: เพื่อให้ Cloud Monitor (CloudWatch/Stackdriver) อ่านง่าย
    - Console Output: ส่งออก stdout/stderr
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    
    # ถ้าเป็น Prod อยากได้ JSON (แต่เพื่อความง่าย ใช้ Format ธรรมดาที่อ่านง่ายไปก่อนสำหรับ Tunnel)
    # ถ้าต้องการ JSON จริงๆ ต้องลง library 'python-json-logger' เพิ่ม
    # ตอนนี้ขอใช้ Format มาตรฐานแต่มี timestamp ชัดเจน
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # ล้าง handler เดิม (ถ้ามี) แล้วใส่ใหม่
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
    
    # ปิด Log รกๆ ของ Third-party บางตัว
    logging.getLogger("uvicorn.access").disabled = False
