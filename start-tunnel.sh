#!/bin/bash
set -e

echo "🐳 Starting Docker services..."
docker compose up -d frontend backend db minio adminer ai_service

echo ""
echo "✅ Docker services started!"
echo ""
echo "🌍 Starting Cloudflare Tunnel..."
echo "   📡 submarines.app         → Frontend"
echo "   📡 api.submarines.app     → Backend API"
echo "   📡 db.submarines.app      → Adminer (Database UI)"
echo "   📡 storage.submarines.app → MinIO Console"
echo "   📡 ai.submarines.app      → AI Detection Service"
echo ""
# Load environment variables from .env if it exists
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# --- Database Selection Logic ---
COMPOSE_PROFILES=""
DISPLAY_DB_INFO=""

if [ "$DB_SOURCE" = "local" ]; then
  echo "🔌 Using LOCAL Database (Docker)..."
  export DATABASE_URL=${LOCAL_DATABASE_URL}
  # Enable local_db profile
  COMPOSE_PROFILES="--profile local_db"
  
  DISPLAY_DB_INFO="
   🗄️ Database UI: http://localhost:8080
      - System:   PostgreSQL (Local)
      - Server:   db
      - User:     ${DB_USER}
      - Pass:     ${DB_PASSWORD}
      - Database: ${DB_NAME}
   🐘 Postgres DB:   localhost:5433"
else
  echo "☁️  Using CLOUD Database (Supabase)..."
  export DATABASE_URL=${CLOUD_DATABASE_URL}
  # No local_db profile needed
  
  DISPLAY_DB_INFO="
   ☁️  Cloud DB:    Supabase (Singapore)
   🔗 Region:      ap-southeast-1"
fi

echo "🐳 Starting Docker services..."
# Pass the correct DATABASE_URL to docker compose
docker compose $COMPOSE_PROFILES up -d frontend backend minio ai_service

echo ""
echo "✅ Docker services started!"
echo ""
echo "🌍 Starting Cloudflare Tunnel..."
echo "   📡 submarines.app         → Frontend"
echo "   📡 api.submarines.app     → Backend API"
echo "   📡 db.submarines.app      → Adminer (Database UI)"
echo "   📡 storage.submarines.app → MinIO Console"
echo "   📡 ai.submarines.app      → AI Detection Service"
echo ""
echo "🏠 Localhost Access (For Testing):"
echo "   💻 Frontend:    http://localhost:5173"
echo "   ⚙️ Backend API: http://localhost:8000"
echo "   🧠 AI Service:  http://localhost:8001"
echo "${DISPLAY_DB_INFO}"
echo "   📦 MinIO Console: http://localhost:9001 (User: ${MINIO_ROOT_USER:-admin}, Pass: ${MINIO_ROOT_PASSWORD:-password})"
echo ""

cloudflared tunnel run submarine-tunnel
