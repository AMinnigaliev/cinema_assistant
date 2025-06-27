import json
import os

import pytest
import spacy


@pytest.mark.skipif()
def test_search_movies(search_tags: dict[str, str], model_path: str) -> None:
    """
    Тест: извлечение названия фильма из datasets.

    @type search_tags: dict[str, str]
    @param search_tags: Теги ner_model.
    @type model_path: str
    @param model_path: Путь к директории ner_model.
    @rtype: None
    @return:
    """
    found_movies = list()

    try:
        nlp = spacy.load(model_path)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_for_tests.json"), "r") as fp:
            test_datasets = json.load(fp)

        for test_dataset in test_datasets:
            for ent in nlp(test_dataset).ents:
                if ent.label_ == search_tags.get("movie", "MOVIE"):
                    found_movies.append(ent.text)

        assert len(found_movies) > 0

    except FileNotFoundError:
        pass
