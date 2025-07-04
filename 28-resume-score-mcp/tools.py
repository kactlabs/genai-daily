import os
import fitz  # PyMuPDF
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from sentence_transformers import SentenceTransformer
from typing import List

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Qdrant client (local)
qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "resumes"

# Setup collection if not exists
def setup_collection():
    if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qdrant_models.VectorParams(
                size=384,
                distance=qdrant_models.Distance.COSINE
            )
        )

setup_collection()

# Extract text from PDF
def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()

# Add a resume to Qdrant
def index_resume(pdf_path: str) -> str:
    text = extract_text(pdf_path)
    embedding = model.encode(text).tolist()
    qdrant.upload_points(
        collection_name=COLLECTION_NAME,
        points=[qdrant_models.PointStruct(
            id=pdf_path,
            vector=embedding,
            payload={"path": pdf_path, "content": text[:1000]}
        )]
    )
    return f"✅ Indexed: {pdf_path}"

# Search resumes with a job description
def search_resumes(job_description: str, top_k: int = 3) -> List[str]:
    query_vec = model.encode(job_description).tolist()
    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=top_k
    )
    return [f"{hit.payload['path']} (score: {hit.score:.2f})" for hit in hits]
