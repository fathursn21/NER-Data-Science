import re
import json
import spacy
from spacy.util import filter_spans
from src.pipeline.config import TARGET_LABELS, DOMAIN_ORGS, DOMAIN_GPES, NOISE_PATTERNS

def build_clean_ground_truth(text, doc):
    candidate_spans = []

    for org in DOMAIN_ORGS:
        for m in re.finditer(rf"(?<!\w){re.escape(org)}(?!\w)", text):
            sp = doc.char_span(m.start(), m.end(), label="ORG", alignment_mode="contract")
            if sp is not None:
                candidate_spans.append(sp)

    for gpe in DOMAIN_GPES:
        for m in re.finditer(rf"(?<!\w){re.escape(gpe)}(?!\w)", text):
            sp = doc.char_span(m.start(), m.end(), label="GPE", alignment_mode="contract")
            if sp is not None:
                candidate_spans.append(sp)

    for ent in doc.ents:
        s_text = ent.text.strip()
        lbl = ent.label_
        if NOISE_PATTERNS.match(s_text) or s_text.startswith("RM"):
            continue
        if len(s_text) > 20 and any("\u4e00" <= c <= "\u9fff" for c in s_text):
            continue
        if lbl in {"ORG", "PERSON"} and len(s_text.split()) >= 5:
            continue
        if s_text in DOMAIN_ORGS or s_text == "Bursa":
            lbl = "ORG"
        elif s_text in DOMAIN_GPES:
            lbl = "GPE"

        if lbl in TARGET_LABELS:
            sp = doc.char_span(ent.start_char, ent.end_char, label=lbl, alignment_mode="contract")
            if sp is not None:
                candidate_spans.append(sp)

    final_spans = filter_spans(candidate_spans)
    entities = [
        {"text": s.text, "label": s.label_, "start": s.start_char, "end": s.end_char}
        for s in sorted(final_spans, key=lambda x: x.start_char)
    ]
    return entities
