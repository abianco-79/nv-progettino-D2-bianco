#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "  MinIO PA Data Lake — teardown"
echo "═══════════════════════════════════════════════════════════════"

echo "Scegli modalità:"
echo "  1) Soft — ferma i container ma mantieni i dati (volume intatto)"
echo "  2) Hard — ferma i container E distruggi il volume (dati persi)"
read -p "Scelta [1/2]: " scelta

if [ "$scelta" = "2" ]; then
    echo "[HARD] docker compose down -v ..."
    docker compose down -v
    echo "✓ Container e volume rimossi."
else
    echo "[SOFT] docker compose down ..."
    docker compose down
    echo "✓ Container fermati. Il volume minio-data è intatto."
fi
