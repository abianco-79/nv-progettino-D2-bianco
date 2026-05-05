#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  MinIO PA Data Lake — avvio"
echo "═══════════════════════════════════════════════════════════════"

# Avvia MinIO in background
echo "[1/3] Avvio container MinIO..."
docker compose up -d minio

# Aspetta che MinIO sia healthy
echo "[2/3] Attendo che MinIO sia pronto..."
until docker compose exec minio curl -sf http://localhost:9000/minio/health/live; do
    echo "  ... ancora in attesa"
    sleep 2
done
echo "  MinIO è pronto!"

# Esegui lo script Python
echo "[3/3] Eseguo upload e analisi..."
docker compose run --rm client python src/upload.py

echo ""
echo "✓ Setup completato!"
echo "  Console MinIO: http://localhost:9001"
echo "  Credenziali:   vedi .env"
