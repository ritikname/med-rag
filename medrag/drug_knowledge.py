from itertools import combinations

# Very tiny demo knowledge base. Extend for real use.
INTERACTIONS = {
    frozenset(["warfarin", "aspirin"]): "Increased bleeding risk.",
    frozenset(["metformin", "contrast dye"]): "Risk of lactic acidosis; hold metformin pre-contrast.",
    frozenset(["ACE inhibitor", "spironolactone"]): "Hyperkalemia risk; monitor potassium.",
    frozenset(["SSRI", "triptan"]): "Serotonin syndrome risk; use caution.",
}

CONTRAINDICATIONS = {
    ("beta blocker", "asthma"): "May worsen bronchospasm; prefer cardioselective agents or alternatives.",
    ("NSAID", "peptic ulcer"): "Risk of bleeding/exacerbation; avoid or add gastroprotection.",
}

def check_interactions(meds: list[str]) -> list[str]:
    meds_lower = [m.lower() for m in meds]
    notes = []
    for a, b in combinations(meds_lower, 2):
        note = INTERACTIONS.get(frozenset([a, b]))
        if note:
            notes.append(f"{a} + {b}: {note}")
    return notes

def check_contraindications(meds: list[str], conditions: list[str]) -> list[str]:
    notes = []
    for m in meds:
        for c in conditions:
            note = CONTRAINDICATIONS.get((m.lower(), c.lower()))
            if note:
                notes.append(f"{m} with {c}: {note}")
    return notes