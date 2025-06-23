from collections import defaultdict

import spacy

from core import config, logger


class AssistantModelWorkerMixin:
    """Mixin - работа с NLP-моделью."""

    @staticmethod
    def named_entity_recognition(text: str | None) -> dict[str, list[str]] | None:
        """
        Обработка входящего текста, поиск по label.

        @type text: str | None
        @param text:
        @rtype ents_by_types: dict[str, list[str]] | None
        @return ents_by_types:
        """
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
