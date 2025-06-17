from schemas.movies_schemas.genre_models import GenreModel


class GenreRules:

    @classmethod
    async def genre_transformation_data_rule(
            cls, obj_data: dict
    ) -> GenreModel:
        genre_es_model = GenreModel(**obj_data)

        genre_es_model.was_enrich = True
        genre_es_model.was_convert = True

        return genre_es_model
