import os
from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from pathlib import Path
from utils import load_config
from anonymize import anonymize_text

# In retriever.py, modify the PDF loading:
def load_pdf_texts(paths: List[str]) -> List[Dict]:
    docs = []
    for p in paths:
        print(f"📖 Reading {p}")
        try:
            if not os.path.exists(p):  # ADD THIS CHECK
                print(f"⚠️ File not found: {p}")
                continue

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(text_len, start + chunk_size)
        # Avoid slicing the whole text repeatedly
        chunks.append(text[start:end].strip())
        start += chunk_size - chunk_overlap  # move forward safely
        if start < 0:  # sanity check
            start = 0

    return [c for c in chunks if c]


def build_or_load_collection(cfg: Dict):
    client = chromadb.PersistentClient(path=cfg["chroma_dir"])
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=cfg["embedding_model"]
    )
    return client, client.get_or_create_collection("medrag", embedding_function=embed_fn)

def ingest_folder(folder: str, cfg: Dict):
    client, col = build_or_load_collection(cfg)
    pdfs = list(Path(folder).glob("**/*.pdf"))
    print(f"📂 Found {len(pdfs)} PDFs in {folder}: {[p.name for p in pdfs]}")
    texts = load_pdf_texts([str(p) for p in pdfs])

    ids, metadatas, docs = [], [], []
    for i, d in enumerate(texts):
        chunks = chunk_text(d["text"], cfg["chunk_size"], cfg["chunk_overlap"])
        print(f"➡️ {os.path.basename(d['path'])}: {len(chunks)} chunks")
        for j, ch in enumerate(chunks):
            if cfg.get("anonymize", True):
                ch = anonymize_text(ch)
            ids.append(f"{i}-{j}-{os.path.basename(d['path'])}")
            metadatas.append({"source": d["path"], "chunk": j})
            docs.append(ch)

    if docs:
        col.upsert(ids=ids, metadatas=metadatas, documents=docs)
        print(f"📊 Upserted {len(docs)} chunks to Chroma")
    else:
        print("⚠️ No documents ingested")
    return len(docs)

def query(text: str, cfg: Dict, top_k: int = None) -> List[Dict]:
    _, col = build_or_load_collection(cfg)
    res = col.query(query_texts=[text], n_results=top_k or cfg["top_k"])
    return [
        {
            "document": res["documents"][0][i],
            "source": res["metadatas"][0][i].get("source"),
            "chunk": res["metadatas"][0][i].get("chunk"),
            "id": res["ids"][0][i]
        }
        for i in range(len(res["documents"][0]))
    ]
