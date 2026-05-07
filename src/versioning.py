import boto3
import os
from botocore.exceptions import ClientError

ENDPOINT   = "http://minio:9000"
ACCESS_KEY = os.environ["MINIO_ROOT_USER"]
SECRET_KEY = os.environ["MINIO_ROOT_PASSWORD"]
BUCKET     = "pa-datalake"

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

# ── 1. Attiva versioning sul bucket ─────────────────────────────────────────
def attiva_versioning():
    s3.put_bucket_versioning(
        Bucket=BUCKET,
        VersioningConfiguration={"Status": "Enabled"},
    )
    risposta = s3.get_bucket_versioning(Bucket=BUCKET)
    print(f"[VERSIONING] Stato: {risposta.get('Status', 'non attivo')}")

# ── 2. Carica due volte lo stesso file con status HTTP ───────────────────────
def doppio_upload():
    key = "2025/open-data/POSAS_it_Comuni.csv"

    print(f"\n[UPLOAD v1] Carico {key} prima volta...")
    with open("data/POSAS_it_Comuni.csv", "rb") as f:
        risposta = s3.put_object(
            Bucket=BUCKET, Key=key, Body=f,
            Metadata={"versione": "v1", "nota": "caricamento iniziale"}
        )
    status = risposta["ResponseMetadata"]["HTTPStatusCode"]
    print(f"  → VersionId: {risposta['VersionId']}  [HTTP {status}]")

    print(f"\n[UPLOAD v2] Carico {key} seconda volta (simula aggiornamento)...")
    with open("data/POSAS_it_Comuni.csv", "rb") as f:
        risposta = s3.put_object(
            Bucket=BUCKET, Key=key, Body=f,
            Metadata={"versione": "v2", "nota": "aggiornamento simulato"}
        )
    status = risposta["ResponseMetadata"]["HTTPStatusCode"]
    print(f"  → VersionId: {risposta['VersionId']}  [HTTP {status}]")

# ── 3. Lista tutte le versioni ───────────────────────────────────────────────
def lista_versioni():
    print(f"\n── Versioni di 2025/open-data/POSAS_it_Comuni.csv ──────────────")
    risposta = s3.list_object_versions(
        Bucket=BUCKET,
        Prefix="2025/open-data/POSAS_it_Comuni.csv"
    )
    for v in risposta.get("Versions", []):
        latest = "← LATEST" if v["IsLatest"] else ""
        print(f"  VersionId:     {v['VersionId']}")
        print(f"  LastModified:  {v['LastModified']}")
        print(f"  Size:          {v['Size'] / 1024:.1f} KB  {latest}")
        print()

# ── 4. Scarica una versione specifica ────────────────────────────────────────
def scarica_versione_precedente():
    risposta = s3.list_object_versions(
        Bucket=BUCKET,
        Prefix="2025/open-data/POSAS_it_Comuni.csv"
    )
    versioni = sorted(
        [v for v in risposta.get("Versions", []) if v["VersionId"] != "null"],
        key=lambda x: x["LastModified"]
    )
    if len(versioni) < 2:
        print("[SKIP] Meno di 2 versioni con VersionId disponibili")
        return

    v_precedente = versioni[0]
    print(f"[DOWNLOAD] Scarico versione precedente: {v_precedente['VersionId']}")
    s3.download_file(
        BUCKET,
        "2025/open-data/POSAS_it_Comuni.csv",
        "/tmp/comuni_v_precedente.csv",
        ExtraArgs={"VersionId": v_precedente["VersionId"]}
    )
    print(f"[OK] File scaricato in /tmp/comuni_v_precedente.csv")

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("═══════════════════════════════════════════════════════════════")
    print("  MinIO — Versioning demo")
    print("═══════════════════════════════════════════════════════════════\n")
    attiva_versioning()
    doppio_upload()
    lista_versioni()
    scarica_versione_precedente()
    print("\n[DONE] Versioning demo completato.")
