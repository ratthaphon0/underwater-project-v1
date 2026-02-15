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

cloudflared tunnel run submarine-tunnel
