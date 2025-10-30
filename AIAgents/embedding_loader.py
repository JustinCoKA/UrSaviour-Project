# embedding_loader.py
import os
import io
import pandas as pd
from PyPDF2 import PdfReader
from rag_engine import get_embedding, chroma_client, COLLECTION_NAME
import aws_connector

collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
DATA_DIR = "data"


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join([page.extract_text() or "" for page in reader.pages])


def load_data_to_chroma():
    """Embed and store all CSV/PDF data into Chroma.

    This function prefers streaming data directly from S3 (no local download).
    If no S3 objects are found it falls back to reading the local `data/` dir.
    """
    # Ensure local dir exists for fallback compatibility
    os.makedirs(DATA_DIR, exist_ok=True)

    existing_ids = set(collection.get().get("ids", []))

    # Try S3 first
    try:
        keys = aws_connector.list_s3_data_keys()
    except Exception:
        keys = []

    if keys:
        for key in keys:
            obj_id = key
            if obj_id in existing_ids:
                continue
            try:
                data_bytes = aws_connector.stream_s3_object_bytes(key)
                if key.lower().endswith('.csv'):
                    # pandas accepts a file-like object
                    df = pd.read_csv(io.BytesIO(data_bytes))
                    text = df.to_string()
                else:  # assume pdf
                    text = extract_text_from_pdf_bytes(data_bytes)

                emb = get_embedding(text)
                collection.add(documents=[text], embeddings=[emb], ids=[obj_id])
                print(f"📚 Added {key} to Chroma.")
            except Exception as e:
                print(f"⚠️ Failed to process {key}: {e}")

        return

    # Fallback: process files from local DATA_DIR
    existing_ids = set(collection.get().get("ids", []))
    for file_name in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file_name)
        if file_name in existing_ids:
            continue

        try:
            # Extract content
            if file_name.lower().endswith(".csv"):
                df = pd.read_csv(file_path)
                text = df.to_string()
            elif file_name.lower().endswith(".pdf"):
                reader = PdfReader(file_path)
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
            else:
                continue

            # Generate embedding and store
            emb = get_embedding(text)
            collection.add(documents=[text], embeddings=[emb], ids=[file_name])
            print(f"📚 Added {file_name} to Chroma.")
        except Exception as e:
            print(f"⚠️ Failed to process {file_name}: {e}")
