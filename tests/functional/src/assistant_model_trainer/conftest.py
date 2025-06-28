import os

import pytest


@pytest.fixture
def search_tags() -> dict[str, str]:
    """
    Fixture - теги ner_model.

    @rtype: dict[str, str]
    @return:
    """
    return {"movie": "MOVIE"}


@pytest.fixture
def model_path() -> str:
    """
    Fixture - путь к директории ner_model.

    @rtype: str
    @return:
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "movie_ner_model")
