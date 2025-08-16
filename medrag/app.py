import os
import json
import gradio as gr
from utils import load_config, simple_sentence_split
from anonymize import anonymize_text, anonymize_patient_record
from retriever import ingest_folder, query
from drug_knowledge import check_interactions, check_contraindications
from icd_snomed import standardize_diagnoses

# Optional OpenAI generation
USE_OPENAI = False
try:
    from openai import OpenAI
    if os.getenv("OPENAI_API_KEY"):
        USE_OPENAI = True
        client = OpenAI()
except Exception:
    USE_OPENAI = False

cfg = load_config()

# ------------------------
# Functions for app logic
# ------------------------

def ingest_pdfs(lit_dir, gl_dir):
    n1 = ingest_folder(lit_dir, cfg)
    n2 = ingest_folder(gl_dir, cfg)
    return f"Ingested chunks — literature: {n1}, guidelines: {n2}"

def clinical_question_app(
    question,
    patient_json,
    diagnoses_csv,
    meds_csv,
    conditions_csv
):
    hits = query(question, cfg, top_k=cfg["top_k"])
    
    context_text = "\n\n".join([h["document"] for h in hits])
    
    bullets = simple_sentence_split(context_text)[:8]
    base_answer = " • " + "\n • ".join(bullets) if bullets else "No context found."
    
    # Patient info handling
    patient_text = ""
    standardized = []
    interaction_warns = []
    contraindication_warns = []

    if patient_json.strip():
        try:
            record = json.loads(patient_json)
            record = anonymize_patient_record(record)
            patient_text = json.dumps(record, indent=2)
        except Exception:
            patient_text = anonymize_text(patient_json)
    
    dx = [d.strip() for d in diagnoses_csv.split(",") if d.strip()]
    meds = [m.strip() for m in meds_csv.split(",") if m.strip()]
    conds = [c.strip() for c in conditions_csv.split(",") if c.strip()]

    standardized = standardize_diagnoses(dx)
    interaction_warns = check_interactions(meds)
    contraindication_warns = check_contraindications(meds, conds)

    final_answer = base_answer
    if USE_OPENAI:
        prompt = f"""You are a medical assistant. Given the clinical question, retrieved evidence and patient info,
draft a concise evidence-based recommendation. Cite policy/guideline names if present in context.
If you are uncertain, state that explicitly.

Question: {question}

Patient (anonymized): {patient_text}

Context:
{context_text}

Provide a short recommendation followed by 3-5 bullet points of supporting evidence from the context.
"""
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt}],
                temperature=0.2,
            )
            final_answer = resp.choices[0].message.content
        except Exception:
            final_answer = base_answer + "\n\n(OpenAI generation failed; falling back to extractive summary.)"

    safety_warnings = interaction_warns + contraindication_warns
    return final_answer, patient_text, json.dumps(standardized, indent=2), "\n".join(safety_warnings)

# ------------------------
# Gradio UI
# ------------------------

with gr.Blocks() as demo:
    gr.Markdown("🩺 **MedRAG — Medical Literature RAG**")
    
    with gr.Tab("Ingestion"):
        lit_dir = gr.Textbox(label="Literature PDF folder", value="data/literature")
        gl_dir = gr.Textbox(label="Guidelines PDF folder", value="data/guidelines")
        ingest_btn = gr.Button("Ingest / Rebuild Index")
        ingest_output = gr.Textbox(label="Status")
        ingest_btn.click(ingest_pdfs, inputs=[lit_dir, gl_dir], outputs=ingest_output)

    with gr.Tab("Clinical Question"):
        with gr.Row():
            with gr.Column(scale=2):
                question = gr.Textbox(label="Enter your clinical question", lines=5,
                                      value="In a hypertensive adult with T2DM, what initial therapy is recommended? Any drug-interaction concerns?")
                patient_json = gr.Textbox(label="Paste anonymized patient JSON (or plain text)", lines=5)
                diagnoses_csv = gr.Textbox(label="Comma-separated diagnoses", value="Hypertension, Type 2 diabetes mellitus")
                meds_csv = gr.Textbox(label="Comma-separated medications", value="ACE inhibitor, metformin")
                conditions_csv = gr.Textbox(label="Comma-separated conditions for contraindication checks", value="asthma")
                submit_btn = gr.Button("Retrieve & Recommend")
            with gr.Column(scale=1):
                final_answer_out = gr.Textbox(label="Recommendation", lines=10)
                patient_out = gr.Textbox(label="Patient (Anonymized)", lines=10)
                standardized_out = gr.Textbox(label="Diagnosis Standardization (ICD10 / SNOMED)", lines=5)
                safety_out = gr.Textbox(label="Safety Checks", lines=5)
        
        submit_btn.click(
            clinical_question_app,
            inputs=[question, patient_json, diagnoses_csv, meds_csv, conditions_csv],
            outputs=[final_answer_out, patient_out, standardized_out, safety_out]
        )

demo.launch(server_name="0.0.0.0", server_port=7860)
