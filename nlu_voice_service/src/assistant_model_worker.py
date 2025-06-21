from collections import defaultdict

import spacy

from core import config, logger


class AssistantModelWorkerMixin:

    @staticmethod
    def named_entity_recognition(text: str | None) -> dict[str, list[str]] | None:
        if text:
            nlp = spacy.load(config.model_dir_path)
            doc = nlp(text)

            ents_by_types = defaultdict(list)
            for ent in doc.ents:
                if ent.label_ in config.model_labels:
                    ents_by_types[ent.label_].append(ent.text)

            if ents_by_types:
                logger.debug(f"[NLP] found entities by types: {ents_by_types}")

            else:
                logger.debug(f"[NLP] not found entities by text: {text}")

            return ents_by_types

        return None
