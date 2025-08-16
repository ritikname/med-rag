import os
import re
from typing import List
from dotenv import load_dotenv
import yaml

def load_config(path: str = "config.yaml") -> dict:
    load_dotenv(override=True)
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    # allow env overrides
    cfg["embedding_model"] = os.getenv("EMBEDDING_MODEL", cfg.get("embedding_model"))
    cfg["chroma_dir"] = os.getenv("CHROMA_DIR", cfg.get("chroma_dir"))
    return cfg

def simple_sentence_split(text: str) -> List[str]:
    # naive splitter that keeps punctuation
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]