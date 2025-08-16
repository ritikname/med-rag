import os
import json
from typing import List
import streamlit as st
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

st.set_page_config(page_title="MedRAG: Clinical Evidence Assistant", layout="wide")
st.title("🩺 MedRAG — Medical Literature RAG")

cfg = load_config()

with st.sidebar:
    st.header("Ingestion")
    lit_dir = st.text_input("Literature PDF folder", value="data/literature")
    gl_dir = st.text_input("Guidelines PDF folder", value="data/guidelines")
    if st.button("Ingest / Rebuild Index"):
        n1 = ingest_folder(lit_dir, cfg)
        n2 = ingest_folder(gl_dir, cfg)
        st.success(f"Ingested chunks — literature: {n1}, guidelines: {n2}")
    st.markdown("---")
    st.subheader("Patient Data")
    patient_json = st.text_area("Paste anonymized patient JSON (or plain text)")
    diagnoses_csv = st.text_input("Comma-separated diagnoses (for ICD/SNOMED)", value="Hypertension, Type 2 diabetes mellitus")
    meds_csv = st.text_input("Comma-separated medications", value="ACE inhibitor, metformin")
    conditions_csv = st.text_input("Comma-separated conditions for contraindication checks", value="asthma")

col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Clinical Question")
    q = st.text_area("Enter your clinical question", height=120, value="In a hypertensive adult with T2DM, what initial therapy is recommended? Any drug-interaction concerns?")
    if st.button("Retrieve & Recommend"):
        hits = query(q, cfg, top_k=cfg["top_k"])
        st.write("### Retrieved Context")
        for h in hits:
            with st.expander(f"Source: {h['source']} — chunk {h['chunk']}"):
                st.write(h["document"])

        # Compose a naive answer from contexts, optionally refine with OpenAI
        context_joined = "\n\n".join([h["document"] for h in hits])
        bullets = simple_sentence_split(context_joined)[:8]
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
                # treat as plain text and anonymize
                patient_text = anonymize_text(patient_json)

        dx = [d.strip() for d in diagnoses_csv.split(",") if d.strip()]
        meds = [m.strip() for m in meds_csv.split(",") if m.strip()]
        conds = [c.strip() for c in conditions_csv.split(",") if c.strip()]

        standardized = standardize_diagnoses(dx)
        interaction_warns = check_interactions(meds)
        contraindication_warns = check_contraindications(meds, conds)

        # Optionally refine with OpenAI if key is set
        final_answer = base_answer
        if USE_OPENAI:
            prompt = f"""You are a medical assistant. Given the clinical question, retrieved evidence and patient info,
draft a concise evidence-based recommendation. Cite policy/guideline names if present in context.
If you are uncertain, state that explicitly.

Question: {q}

Patient (anonymized): {patient_text}

Context:
{context_joined}

Provide a short recommendation followed by 3-5 bullet points of supporting evidence from the context.
"""
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}],
                    temperature=0.2,
                )
                final_answer = resp.choices[0].message.content
            except Exception as e:
                final_answer = base_answer + f"\n\n(OpenAI generation failed; falling back to extractive summary.)"

        st.write("### Recommendation")
        st.write(final_answer)

        with st.expander("Patient (Anonymized)"):
            st.code(patient_text or "(none)", language="json")

        with st.expander("Diagnosis Standardization (ICD10 / SNOMED)"):
            st.json(standardized)

        if interaction_warns or contraindication_warns:
            st.warning("#### Safety Checks")
            for w in interaction_warns + contraindication_warns:
                st.write("- " + w)

with col2:
    st.subheader("Settings")
    st.json(cfg)
    st.info("Tip: Place PDFs in data/literature and data/guidelines, then click 'Ingest'. Paste patient data (anonymized or raw).")

st.caption("For clinical education/demo only — not for real patient care.")
