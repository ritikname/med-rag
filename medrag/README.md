# MedRAG — Medical Literature RAG (Healthcare)

An end-to-end Retrieval-Augmented Generation (RAG) system that ingests medical literature and clinical guidelines,
integrates anonymized patient data, and surfaces evidence-backed recommendations to assist healthcare professionals.

> **Disclaimer:** Educational demo only. Not for real patient care or medical decisions.

## Features
- PDF ingestion of medical journals & guidelines (place PDFs in `data/literature` and `data/guidelines`).
- Patient data entry (JSON or plain text) with basic PHI anonymization.
- Vector retrieval with ChromaDB and Sentence-Transformers embeddings.
- Optional LLM generation via OpenAI (`OPENAI_API_KEY`) or extractive fallback.
- Safety checks: simple drug–drug interactions and contraindications.
- ICD-10 & SNOMED demo mappings for diagnoses.
- RAGAS evaluation script for basic metrics.

## Tech Stack
- Embeddings: HuggingFace Sentence-Transformers (`all-MiniLM-L6-v2` by default)
- Vector DB: Chroma (persistent)
- App: Streamlit UI
- Parsing: `pypdf`
- Optional Generation: OpenAI API
- Evaluation: RAGAS

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (Optional) set your OpenAI key for answer generation
cp .env.example .env
# edit .env to add OPENAI_API_KEY
```

### Data
- Add PDF files to:
  - `data/literature/`
  - `data/guidelines/`

### Build the vector index
```bash
python ingest.py --literature data/literature --guidelines data/guidelines
```

### Run the app
```bash
streamlit run app.py
```

Open the local URL Streamlit prints in the console.

### Evaluate (RAGAS)
> First index the PDFs. Then run:
```bash
python eval_rag.py
```

## Project Structure
```
medrag/
├── app.py
├── ingest.py
├── retriever.py
├── anonymize.py
├── icd_snomed.py
├── drug_knowledge.py
├── utils.py
├── eval_rag.py
├── config.yaml
├── requirements.txt
├── .env.example
├── data/
│   ├── literature/
│   ├── guidelines/
│   └── patients/
└── storage/
```

## Notes
- Chunking can be tuned in `config.yaml`.
- This repo uses a very small interaction/contraindication KB for demonstration. Replace it with a clinical database (Lexicomp, Micromedex) in real deployments.
- Patient anonymization here is regex-based and not production-grade — integrate with a proper PHI redaction pipeline for real use.

## License
MIT