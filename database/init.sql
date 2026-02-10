-- EXTENSION OPEN: UUID และ Timezone
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- 1. Table: monitoring_sessions (รอบการเดินเรือ)
-- =============================================
CREATE TABLE IF NOT EXISTS monitoring_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    location_name VARCHAR(255),
    notes TEXT
);

-- =============================================
-- 2. Table: water_telemetry (Time-series Data)
-- =============================================
CREATE TABLE IF NOT EXISTS water_telemetry (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    lat FLOAT,
    lng FLOAT,
    depth FLOAT,
    temperature FLOAT,
    ph FLOAT,
    dissolved_oxygen FLOAT,
    ec_tds FLOAT,
    turbidity FLOAT,
    CONSTRAINT fk_session_telemetry FOREIGN KEY (session_id) REFERENCES monitoring_sessions(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_telemetry_time ON water_telemetry(session_id, timestamp);

-- =============================================
-- 3. Table: fish_detections (AI Vision Result)
-- =============================================
CREATE TABLE IF NOT EXISTS fish_detections (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    raw_image_path TEXT NOT NULL,
    enhanced_image_path TEXT,
    fish_count INTEGER DEFAULT 0,
    detection_metadata JSONB,
    health_status VARCHAR(100),
    CONSTRAINT fk_session_vision FOREIGN KEY (session_id) REFERENCES monitoring_sessions(id) ON DELETE CASCADE
);

-- =============================================
-- 4. Table: water_predictions (Forecast)
-- =============================================
CREATE TABLE IF NOT EXISTS water_predictions (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL, -- ✅ 1. เพิ่มบรรทัดนี้ (เพื่อเก็บ ID การเดินทาง)
    base_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    predict_for_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    parameter_name VARCHAR(50) NOT NULL,
    predicted_value FLOAT NOT NULL,
    confidence_interval FLOAT,
    model_version VARCHAR(50),
    CONSTRAINT fk_session_predictions FOREIGN KEY (session_id) REFERENCES monitoring_sessions(id) ON DELETE CASCADE
);

-- =============================================
-- 5. Table: tilapia_lifecycle_standards (Master Data)
-- =============================================
CREATE TABLE IF NOT EXISTS tilapia_lifecycle_standards (
    stage_name VARCHAR(100) PRIMARY KEY,
    min_temp FLOAT, max_temp FLOAT,
    min_do FLOAT,
    ph_range_min FLOAT, ph_range_max FLOAT,
    alert_threshold JSONB
);

-- Seed Data 
INSERT INTO tilapia_lifecycle_standards (stage_name, min_temp, max_temp, min_do, ph_range_min, ph_range_max)
VALUES ('Adult', 20.0, 35.0, 3.0, 6.0, 9.0)
ON CONFLICT (stage_name) DO NOTHING;