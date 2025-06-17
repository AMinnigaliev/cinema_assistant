from schemas.movies_schemas.person_models import PersonModel


class PersonRules:

    @classmethod
    async def person_transformation_data_rule(
            cls, obj_data: dict
    ) -> PersonModel:
        person_es_model = PersonModel(**obj_data)

        person_es_model.was_enrich = True
        person_es_model.was_convert = True

        return person_es_model
