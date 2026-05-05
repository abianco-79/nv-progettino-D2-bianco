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
        # Metadati dettagliati tramite head_object
        head = s3.head_object(Bucket=BUCKET, Key=obj["Key"])
        print(f"  KEY:           {obj['Key']}")
        print(f"  size:          {size_kb:.1f} KB")
        print(f"  last-modified: {obj['LastModified']}")
        print(f"  content-type:  {head['ContentType']}")
        print(f"  etag:          {head['ETag']}")
        print()

# ── 4. Download, testata e analisi ──────────────────────────────────────────
def analisi():
    # ── Dataset 1: Popolazione comuni ───────────────────────────────────────
    print("\n── Dataset 1: POSAS_it_Comuni.csv ──────────────────────────────")
    key1  = "2025/open-data/POSAS_it_Comuni.csv"
    local1 = "/tmp/comuni_download.csv"
    s3.download_file(BUCKET, key1, local1)
    print(f"[DOWNLOAD] s3://{BUCKET}/{key1} → {local1}")

    df1 = pd.read_csv(local1, sep=";", encoding="utf-8-sig")
    print(f"\nColonne: {list(df1.columns)}")
    print(f"Righe:   {len(df1)}")

    print("\n── Testata (prime 5 righe) ─────────────────────────────────────")
    print(df1.head().to_string(index=False))

    print("\n── describe() ──────────────────────────────────────────────────")
    print(df1.describe())

    print("\n── Top 5 comuni per popolazione ────────────────────────────────")
    top5 = df1.nlargest(5, "Totale")[["Comune", "Totale maschi", "Totale femmine", "Totale"]]
    print(top5.to_string(index=False))

    # ── Dataset 2: Redditi IRPEF ─────────────────────────────────────────────
    print("\n── Dataset 2: Redditi_IRPEF_su_base_comunale_2024.csv ──────────")
    key2   = "2025/open-data/Redditi_e_principali_variabili_IRPEF_su_base_comunale_2024.csv"
    local2 = "/tmp/irpef_download.csv"
    s3.download_file(BUCKET, key2, local2)
    print(f"[DOWNLOAD] s3://{BUCKET}/{key2} → {local2}")

    df2 = pd.read_csv(local2, sep=";", encoding="utf-8-sig")
    print(f"\nColonne totali: {len(df2.columns)}")
    print(f"Righe:          {len(df2)}")

    print("\n── Testata (prime 3 righe, prime 6 colonne) ────────────────────")
    print(df2.iloc[:3, :6].to_string(index=False))

    col_reddito = "Reddito complessivo - Ammontare in euro"
    col_comune  = "Denominazione Comune"
    col_contrib = "Numero contribuenti"
    print("\n── Top 5 comuni per reddito complessivo ────────────────────────")
    top5_irpef = df2.nlargest(5, col_reddito)[[col_comune, col_contrib, col_reddito]]
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
