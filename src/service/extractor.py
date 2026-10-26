import os
import spacy
import src.pipeline.trainer  # Memastikan komponen custom domain_ner_refiner terdaftar di spaCy
from src.pipeline.config import MODEL_SAVE_DIR
from src.pipeline.evaluator import extract_filtered_entities

class NERService:
    def __init__(self):
        self.model_name = "en_core_web_sm"
        self.nlp = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(os.path.join(MODEL_SAVE_DIR, "meta.json")):
            try:
                self.nlp = spacy.load(MODEL_SAVE_DIR)
                self.model_name = "custom-spacy-ner-v1 (fine-tuned)"
                return
            except Exception:
                pass
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = spacy.blank("en")
        if "domain_ner_refiner" not in self.nlp.pipe_names:
            self.nlp.add_pipe("domain_ner_refiner", last=True)
        self.model_name = "custom-spacy-ner-v1 (domain-adapted)"

    def analyze(self, title: str, body: str) -> dict:
        t_clean = title.strip()
        b_clean = body.strip()
        combined_text = f"{t_clean}. {b_clean}" if (t_clean and b_clean) else (t_clean or b_clean)

        preds = extract_filtered_entities(self.nlp, combined_text, apply_post_filter=True)
        entities = [
            {"text": txt, "label": lbl, "start": s, "end": e}
            for (s, e, lbl, txt) in preds
        ]
        return {
            "entities": entities,
            "meta": {
                "entity_count": len(entities),
                "model": self.model_name
            }
        }

ner_service = NERService()
