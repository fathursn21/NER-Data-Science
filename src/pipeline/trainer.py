import re
import time
import random
import spacy
from spacy.language import Language
from spacy.util import minibatch, filter_spans
from spacy.training import Example
from src.pipeline.config import TARGET_LABELS, DOMAIN_ORGS, DOMAIN_GPES, NOISE_PATTERNS, SEED, MODEL_SAVE_DIR

@Language.component("domain_ner_refiner")
def domain_ner_refiner(doc):
    candidate_spans = []
    text = doc.text

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
        if lbl not in TARGET_LABELS:
            continue
        if NOISE_PATTERNS.match(s_text) or s_text.startswith("RM"):
            continue
        if len(s_text) > 20 and any("\u4e00" <= c <= "\u9fff" for c in s_text):
            continue
        if lbl in {"ORG", "PERSON"} and len(s_text.split()) >= 5:
            continue
        if any(s_text.startswith(org + " ") for org in ["Maybank", "CIMB", "Petronas", "Top Glove"]):
            continue
        if s_text == "Bursa":
            lbl = "ORG"
        sp = doc.char_span(ent.start_char, ent.end_char, label=lbl, alignment_mode="contract")
        if sp is not None:
            candidate_spans.append(sp)

    doc.ents = filter_spans(candidate_spans)
    return doc
