"""
video_source.py — Video Source Abstraction Layer

รองรับ 3 ประเภท source ผ่าน string เดียว:
  "0"            → Webcam (laptop camera index 0)
  "fish_video.mp4" → Local video file
  "rtsp://..."   → RTSP stream (Raspberry Pi via MediaMTX)

Usage:
    from video_source import VideoSource

    src = VideoSource.from_env()   # อ่านจาก env VIDEO_SOURCE
    # หรือ
    src = VideoSource("0")         # webcam โดยตรง

    src.open()
    while src.is_open():
        frame = src.read()
        if frame is None:
            continue               # กำลัง reconnect อยู่
        # ... process frame
    src.release()
"""

import cv2
import os
import time
import logging

logger = logging.getLogger(__name__)

# ─── Source Type Detection ─────────────────────────────────────────────────────

def _detect_type(source: str) -> str:
    """แยกประเภท source จาก string"""
    if source.startswith("rtsp://") or source.startswith("rtsps://"):
        return "rtsp"
    try:
        int(source)
        return "webcam"
    except ValueError:
        return "file"


# ─── VideoSource Class ─────────────────────────────────────────────────────────

class VideoSource:
    """
    Unified video source ที่ handle reconnect และ EOF แตกต่างกันตาม type:

    - file   : loop กลับต้นวิดีโออัตโนมัติเมื่อจบ
    - webcam : retry เปิดกล้องสูงสุด MAX_RETRIES ครั้ง ถ้าล้มเหลว raise
    - rtsp   : reconnect อัตโนมัติตลอดเวลา (infinite retry + backoff)
    """

    # จำนวน retry สูงสุดสำหรับ webcam (ไม่ใช่ rtsp)
    WEBCAM_MAX_RETRIES = 5
    WEBCAM_RETRY_DELAY = 2.0   # วินาที

    # Backoff สำหรับ RTSP reconnect
    RTSP_RETRY_DELAY_MIN = 2.0
    RTSP_RETRY_DELAY_MAX = 30.0
    RTSP_RETRY_BACKOFF   = 2.0  # คูณ 2 ทุกครั้งที่ fail

    def __init__(self, source: str):
        """
        Parameters
        ----------
        source : str
            "0"              → webcam index 0
            "/dev/video0"    → webcam device path (Linux)
            "path/to/file"   → video file
            "rtsp://host/path" → RTSP stream
        """
        self.source_str  = source
        self.source_type = _detect_type(source)
        self._cap: cv2.VideoCapture | None = None
        self._rtsp_retry_delay = self.RTSP_RETRY_DELAY_MIN

        logger.info(f"VideoSource init: type={self.source_type}, source='{source}'")

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_env(cls, env_key: str = "VIDEO_SOURCE", default: str = "0") -> "VideoSource":
        """สร้าง VideoSource จาก environment variable"""
        source = os.getenv(env_key, default).strip()
        logger.info(f"VideoSource from env {env_key}='{source}'")
        return cls(source)

    # ── Public API ────────────────────────────────────────────────────────────

    def open(self) -> bool:
        """เปิด source — คืน True ถ้าสำเร็จ"""
        return self._open_cap()

    def is_open(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    def read(self) -> cv2.typing.MatLike | None:
        """
        อ่าน 1 frame

        คืน frame (numpy array) ถ้าสำเร็จ
        คืน None ถ้ากำลัง reconnect อยู่ (caller ควร continue)
        raise RuntimeError ถ้าเปิด source ไม่ได้จริงๆ (เฉพาะ webcam)
        """
        if not self.is_open():
            return self._handle_lost_connection()

        ret, frame = self._cap.read()

        if ret:
            # อ่านสำเร็จ — reset rtsp backoff delay
            self._rtsp_retry_delay = self.RTSP_RETRY_DELAY_MIN
            return frame

        # อ่านไม่ได้ — แยก logic ตาม type
        return self._handle_read_failure()

    def release(self):
        """ปล่อย resource"""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        logger.info("VideoSource released")

    @property
    def fps(self) -> float:
        """FPS ของ source (0.0 ถ้าไม่ทราบ)"""
        if not self.is_open():
            return 0.0
        return self._cap.get(cv2.CAP_PROP_FPS) or 30.0

    @property
    def width(self) -> int:
        if not self.is_open():
            return 0
        return int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self) -> int:
        if not self.is_open():
            return 0
        return int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def info(self) -> dict:
        """คืน dict ข้อมูล source สำหรับ health check / logging"""
        return {
            "source":  self.source_str,
            "type":    self.source_type,
            "is_open": self.is_open(),
            "fps":     self.fps,
            "width":   self.width,
            "height":  self.height,
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    def _open_cap(self) -> bool:
        """
        เปิด VideoCapture ตาม type — ตั้งค่า buffer/transport ให้เหมาะสม
        """
        if self._cap is not None:
            self._cap.release()

        if self.source_type == "rtsp":
            # ใช้ TCP แทน UDP เพื่อเสถียรภาพ และลด buffer เพื่อ latency ต่ำ
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
            cap = cv2.VideoCapture(self.source_str, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        elif self.source_type == "webcam":
            idx = int(self.source_str)
            cap = cv2.VideoCapture(idx)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            # ตั้ง resolution เริ่มต้น (แก้ได้ภายหลัง)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        else:  # file
            cap = cv2.VideoCapture(self.source_str)

        if cap.isOpened():
            self._cap = cap
            logger.info(
                f"VideoSource opened — {self.source_type} "
                f"{self.width}x{self.height} @ {self.fps:.1f}fps"
            )
            return True

        cap.release()
        logger.warning(f"VideoSource failed to open: '{self.source_str}'")
        return False

    def _handle_read_failure(self) -> None:
        """
        จัดการกรณี cap.read() คืน ret=False แยกตาม source type
        คืน None เสมอ (caller ต้อง continue รอ frame ถัดไป)
        """
        if self.source_type == "file":
            logger.info("Video file ended — looping back to start")
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        elif self.source_type == "webcam":
            logger.warning("Webcam read failed — camera disconnected?")
            raise RuntimeError(
                f"Webcam '{self.source_str}' disconnected and cannot recover. "
                "Please check the camera connection."
            )

        else:  # rtsp
            logger.warning(
                f"RTSP stream lost — reconnecting in {self._rtsp_retry_delay:.0f}s ..."
            )
            self._cap.release()
            self._cap = None
            time.sleep(self._rtsp_retry_delay)
            self._reconnect_rtsp()

        return None

    def _handle_lost_connection(self) -> None:
        """
        เรียกเมื่อ is_open() = False ตอน read() (สถานะหลัง reconnect ล้มเหลว)
        """
        if self.source_type == "rtsp":
            logger.warning(
                f"RTSP not open — retrying in {self._rtsp_retry_delay:.0f}s ..."
            )
            time.sleep(self._rtsp_retry_delay)
            self._reconnect_rtsp()
        return None

    def _reconnect_rtsp(self):
        """Reconnect RTSP ด้วย exponential backoff"""
        success = self._open_cap()
        if success:
            logger.info("RTSP reconnected successfully")
            self._rtsp_retry_delay = self.RTSP_RETRY_DELAY_MIN
        else:
            # เพิ่ม delay สำหรับ retry ครั้งถัดไป (backoff)
            self._rtsp_retry_delay = min(
                self._rtsp_retry_delay * self.RTSP_RETRY_BACKOFF,
                self.RTSP_RETRY_DELAY_MAX,
            )
            logger.warning(
                f"RTSP reconnect failed — next retry in {self._rtsp_retry_delay:.0f}s"
            )


# ─── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    source_str = sys.argv[1] if len(sys.argv) > 1 else "0"
    print(f"\n🎥 Testing VideoSource: '{source_str}'")

    src = VideoSource(source_str)
    if not src.open():
        print(f"❌ Cannot open source: '{source_str}'")
        sys.exit(1)

    print(f"✅ Opened: {src.info()}")
    print("   Reading 5 frames...")

    count = 0
    while count < 5:
        frame = src.read()
        if frame is None:
            continue
        count += 1
        h, w = frame.shape[:2]
        print(f"   Frame {count}: {w}x{h}")

    src.release()
    print("✅ Done — VideoSource working correctly\n")
