#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  MinIO PA Data Lake — avvio"
echo "═══════════════════════════════════════════════════════════════"

# Avvia MinIO in background
echo "[1/5] Avvio container MinIO..."
docker compose up -d minio

# Aspetta che MinIO sia healthy
echo "[2/5] Attendo che MinIO sia pronto..."
until docker compose exec minio curl -sf http://localhost:9000/minio/health/live; do
    echo "  ... ancora in attesa"
    sleep 2
done
echo "  MinIO è pronto!"

# Build del client
echo "[3/5] Build immagine client..."
docker compose build client

# Esegui upload e analisi
echo "[4/5] Eseguo upload e analisi..."
docker compose run --rm client python src/upload.py

# Estensioni opzionali
echo "[5/5] Eseguo estensioni opzionali..."
echo "  → Versioning..."
docker compose run --rm client python src/versioning.py
echo "  → Policy read-only..."
docker compose run --rm client python src/policy.py

echo ""
echo "✓ Setup completato!"
echo "  Console MinIO: http://localhost:9001"
echo "  Credenziali:   vedi .env"
