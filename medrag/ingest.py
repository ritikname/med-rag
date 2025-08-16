import argparse
from utils import load_config
from retriever import ingest_folder

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--literature", default="data/literature")
    parser.add_argument("--guidelines", default="data/guidelines")
    args = parser.parse_args()
    cfg = load_config()
    n1 = ingest_folder(args.literature, cfg)
    n2 = ingest_folder(args.guidelines, cfg)
    print(f"Ingested chunks - literature: {n1}, guidelines: {n2}")