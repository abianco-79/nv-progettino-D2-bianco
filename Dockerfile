FROM python:3.11-slim

WORKDIR /app

RUN pip install boto3 pandas

COPY src/ ./src/
COPY data/ ./data/

CMD ["python", "src/upload.py"]
