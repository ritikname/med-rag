import re
from typing import Dict

PHI_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"),
    "mrn": re.compile(r"\b(?:MRN|Patient\s*ID|Record\s*No\.?)\s*[:#]?\s*\w+\b", re.IGNORECASE),
    "date": re.compile(r"\b(?:\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s*\d{4})\b", re.IGNORECASE),
    "address": re.compile(r"\b\d{1,4}\s+[A-Za-z0-9\s]+\s(?:St|Street|Ave|Avenue|Blvd|Road|Rd|Lane|Ln|Way|Drive|Dr)\b", re.IGNORECASE),
    "name": re.compile(r"\b(?:Name|Patient)\s*[:\-]\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"),
}

def anonymize_text(text: str) -> str:
    replaced = text
    for label, pattern in PHI_PATTERNS.items():
        replaced = pattern.sub(f"<{label.upper()}>", replaced)
    return replaced

def anonymize_patient_record(record: Dict) -> Dict:
    clean = {}
    for k, v in record.items():
        if isinstance(v, str):
            clean[k] = anonymize_text(v)
        else:
            clean[k] = v
    return clean