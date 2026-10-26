from collections import defaultdict
from src.pipeline.config import TARGET_LABELS, NOISE_PATTERNS

def extract_filtered_entities(model, text, apply_post_filter=True):
    doc = model(text)
    preds = []
    for ent in doc.ents:
        if ent.label_ not in TARGET_LABELS:
            continue
        if apply_post_filter:
            s_text = ent.text.strip()
            if NOISE_PATTERNS.match(s_text) or s_text.startswith("RM"):
                continue
            if len(s_text) > 20 and any("\u4e00" <= c <= "\u9fff" for c in s_text):
                continue
            if ent.label_ in {"ORG", "PERSON"} and len(s_text.split()) >= 5:
                continue
        preds.append((ent.start_char, ent.end_char, ent.label_, ent.text))
    return preds

def evaluate_exact_span(model, dataset, apply_post_filter=True):
    tp, fp, fn = 0, 0, 0
    per_label = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    errors = []

    for item in dataset:
        text = item["full_text"]
        gold_set = {(e["start"], e["end"], e["label"]) for e in item["entities"]}
        pred_list = extract_filtered_entities(model, text, apply_post_filter=apply_post_filter)
        pred_set = {(s, e, l) for (s, e, l, _) in pred_list}

        tp += len(gold_set & pred_set)
        fp += len(pred_set - gold_set)
        fn += len(gold_set - pred_set)

        for (s, e, l) in (gold_set & pred_set):
            per_label[l]["tp"] += 1
        for (s, e, l) in sorted(pred_set - gold_set):
            per_label[l]["fp"] += 1
            errors.append({"type": "False Positive", "text": text[s:e], "label": l, "article_id": item["original_id"]})
        for (s, e, l) in sorted(gold_set - pred_set):
            per_label[l]["fn"] += 1
            errors.append({"type": "False Negative", "text": text[s:e], "label": l, "article_id": item["original_id"]})

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    label_metrics = {}
    for l, c in per_label.items():
        p = c["tp"] / (c["tp"] + c["fp"]) if (c["tp"] + c["fp"]) > 0 else 0.0
        r = c["tp"] / (c["tp"] + c["fn"]) if (c["tp"] + c["fn"]) > 0 else 0.0
        f = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        label_metrics[l] = {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4), "support": c["tp"] + c["fn"]}

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "per_label": label_metrics,
        "errors": errors
    }
