import spacy
from spacy.tokens import Span

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
                if ent.label_ == config.movie_label and ent.text.lower().startswith("фильм "):
                    offset = 1 if doc[ent.start].lower_ == "фильм" else 0  #  Смещение спана, для пропуска слова 'фильм'

                    # Проверка, в случае, если нет названия фильма
                    if offset and ent.start + offset < ent.end:
                        new_ent = Span(doc, ent.start + offset, ent.end, label=ent.label)
                        ent_by_types[ent.label_]= new_ent.text

                    break

                elif ent.label_ == config.movie_label and not ent.text.lower().startswith("фильм "):
                    ent_by_types[ent.label_] = ent.text
                    break

            if ent_by_types:
                logger.debug(f"[NLP] found entity by types: {ent_by_types}")

            else:
                logger.debug(f"[NLP] not found entities by text: {text}")

            return ent_by_types

        return None
