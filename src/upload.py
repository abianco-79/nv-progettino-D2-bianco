import boto3
import pandas as pd
import os
from botocore.exceptions import ClientError

# ── Configurazione connessione ──────────────────────────────────────────────
ENDPOINT   = "http://minio:9000"
ACCESS_KEY = os.environ["MINIO_ROOT_USER"]
SECRET_KEY = os.environ["MINIO_ROOT_PASSWORD"]
BUCKET     = "pa-datalake"

DATASETS = [
    "data/POSAS_it_Comuni.csv",
    "data/Redditi_e_principali_variabili_IRPEF_su_base_comunale_2024.csv",
]

# ── Client S3 ───────────────────────────────────────────────────────────────
s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

# ── 1. Crea bucket (se non esiste) ──────────────────────────────────────────
def crea_bucket():
    try:
        s3.head_bucket(Bucket=BUCKET)
        print(f"[OK] Bucket '{BUCKET}' esiste già")
    except ClientError:
        s3.create_bucket(Bucket=BUCKET)
        print(f"[OK] Bucket '{BUCKET}' creato")

# ── 2. Upload dei dataset ───────────────────────────────────────────────────
def upload_datasets():
    for path in DATASETS:
        key = "2025/open-data/" + os.path.basename(path)
        s3.upload_file(path, BUCKET, key)
        print(f"[UPLOAD] {path} → s3://{BUCKET}/{key}")

# ── 3. Lista oggetti con metadati ───────────────────────────────────────────
def lista_oggetti():
    print("\n── Oggetti nel bucket ──────────────────────────────────────────")
    risposta = s3.list_objects_v2(Bucket=BUCKET)
    for obj in risposta.get("Contents", []):
        size_kb = obj["Size"] / 1024
        print(f"  {obj['Key']}")
        print(f"    size: {size_kb:.1f} KB  |  last-modified: {obj['LastModified']}")

# ── 4. Download e analisi ───────────────────────────────────────────────────
def analisi():
    print("\n── Analisi: popolazione comuni ─────────────────────────────────")
    key = "2025/open-data/POSAS_it_Comuni.csv"
    local = "/tmp/comuni_download.csv"
    s3.download_file(BUCKET, key, local)
    print(f"[DOWNLOAD] s3://{BUCKET}/{key} → {local}")

    df = pd.read_csv(local, sep=";", encoding="utf-8-sig")
    print(f"\nColonne: {list(df.columns)}")
    print(f"Righe:   {len(df)}")
    print("\n── describe() ──────────────────────────────────────────────────")
    print(df.describe())

    print("\n── Top 5 comuni per popolazione ────────────────────────────────")
    top5 = df.nlargest(5, "Totale")[["Comune", "Totale maschi", "Totale femmine", "Totale"]]
    print(top5.to_string(index=False))

    print("\n── Analisi: redditi IRPEF ──────────────────────────────────────")
    key2 = "2025/open-data/Redditi_e_principali_variabili_IRPEF_su_base_comunale_2024.csv"
    local2 = "/tmp/irpef_download.csv"
    s3.download_file(BUCKET, key2, local2)
    print(f"[DOWNLOAD] s3://{BUCKET}/{key2} → {local2}")

    df2 = pd.read_csv(local2, sep=";", encoding="utf-8-sig")
    print(f"\nColonne totali: {len(df2.columns)}")
    print(f"Righe:          {len(df2)}")

    col_reddito = "Reddito complessivo - Ammontare in euro"
    col_comune  = "Denominazione Comune"
    col_contrib = "Numero contribuenti"
    top5_irpef = (
        df2.nlargest(5, col_reddito)[[col_comune, col_contrib, col_reddito]]
    )
    print("\n── Top 5 comuni per reddito complessivo ────────────────────────")
    print(top5_irpef.to_string(index=False))

# ── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("═══════════════════════════════════════════════════════════════")
    print("  MinIO PA Data Lake — upload & analisi")
    print("═══════════════════════════════════════════════════════════════\n")
    crea_bucket()
    upload_datasets()
    lista_oggetti()
    analisi()
    print("\n[DONE] Script completato con successo.")
EOF
