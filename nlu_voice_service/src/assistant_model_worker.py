import spacy

from core import config, logger


class AssistantModelWorkerMixin:
    """Mixin - работа с NLP-моделью."""

    @staticmethod
    def named_entity_recognition(text: str | None) -> dict[str, str] | None:
        """
        Обработка входящего текста, поиск по label.

        @type text: str | None
        @param text:
        @rtype ent_by_types: dict[str, str] | None
        @return ent_by_types:
        """
        if text:
            nlp = spacy.load(config.model_dir_path)
            doc = nlp(text)

            ent_by_types = dict()
            for ent in doc.ents:
                if ent.label_ in config.model_labels:
                    ent_by_types[ent.label_] = ent.text

            if ent_by_types:
                logger.debug(f"[NLP] found entity by types: {ent_by_types}")

            else:
                logger.debug(f"[NLP] not found entities by text: {text}")

            return ent_by_types

        return None
