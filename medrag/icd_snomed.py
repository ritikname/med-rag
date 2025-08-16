# Simple demo mappings for standardization
ICD10 = {
    "Hypertension": "I10",
    "Type 2 diabetes mellitus": "E11.9",
    "Asthma": "J45.909",
    "Acute myocardial infarction": "I21.9",
}

SNOMED = {
    "Hypertension": "38341003",
    "Type 2 diabetes mellitus": "44054006",
    "Asthma": "195967001",
    "Acute myocardial infarction": "57054005",
}

def standardize_diagnoses(terms):
    out = []
    for t in terms:
        icd = ICD10.get(t)
        snomed = SNOMED.get(t)
        out.append({"term": t, "ICD10": icd, "SNOMED": snomed})
    return out