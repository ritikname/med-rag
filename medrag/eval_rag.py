# Simple RAGAS evaluation demo
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness, context_precision, context_recall
from utils import load_config
from retriever import query

# Tiny toy set for demonstration
QUESTIONS = [
    "What are first-line treatments for hypertension in adults?",
    "How to manage T2DM in CKD stage 3 patients?",
]

REFS = [
    "First-line anti-hypertensives include thiazide diuretics, ACE inhibitors/ARBs, and calcium channel blockers, per major guidelines.",
    "For T2DM with CKD stage 3, metformin may be used with dose adjustment; consider SGLT2 inhibitors for renal protection as per guidelines.",
]

def build_dataset(cfg):
    rows = []
    for q, ref in zip(QUESTIONS, REFS):
        contexts = [hit["document"] for hit in query(q, cfg, top_k=4)]
        # naive answer: return top context
        answer = contexts[0] if contexts else ""
        rows.append({"question": q, "answer": answer, "contexts": contexts, "ground_truth": ref})
    return Dataset.from_pandas(pd.DataFrame(rows))

if __name__ == "__main__":
    cfg = load_config()
    ds = build_dataset(cfg)
    results = evaluate(
        ds,
        metrics=[answer_relevancy, faithfulness, context_precision, context_recall]
    )
    print(results)
    print(results.to_pandas())