import json

from core.logger import logger
from interface import ESClient_T, RedisStorage_T
from models.movies.pg_models import Base as BaseModel
from models.movies.pg_models import FilmWork, Genre, Person
from schemas import Base as BaseSchema
from transfer.movies.convert_rules import (FilmWorkRules, GenreRules,
                                           PersonRules)


class Convertor:
    """Класс по приведению данных к соответствию схеме индекса."""

    CONCAT = 1

    def __init__(
        self,
        redis_storage: RedisStorage_T,
        pg_session,
        es_client: ESClient_T,
    ):
        self._redis_storage: RedisStorage_T = redis_storage
        self._pg_session = pg_session
        self._es_client: ESClient_T = es_client

    @property
    def redis_storage(self) -> RedisStorage_T:
        return self._redis_storage

    @property
    def pg_session(self):
        return self._pg_session

    @property
    def model_rules(self) -> dict:
        return {
            FilmWork: FilmWorkRules.film_work_transformation_data_rule,
            Person: PersonRules.person_transformation_data_rule,
            Genre: GenreRules.genre_transformation_data_rule,
        }

    @staticmethod
    def get_key_of_rule(model_: BaseModel) -> str:
        return model_.model_name()

    async def run(self) -> None:
        """
        Точка запуска. Этапы:
        - Получение из Storage сущности.
        - Преобразование сущностей в валидный для схемы индекса ES формат
        данных.
        - Сохранение валидных для схемы индекса ES данных в Storage.

        :return None:
        """
        for model_, transformation_rule in self.model_rules.items():
            convert_count = 0
            key_rule = self.get_key_of_rule(model_=model_)
            scan_lst = await self.redis_storage.scan_iter(f"{key_rule}_*")

            if scan_lst:
                logger.info(
                    f"{key_rule}: start convert enrich data(count: "
                    f"{len(scan_lst)})"
                )

            for obj_key_rule in scan_lst:
                obj_ = await self._get_object_data_by_key_rule(
                    obj_key_rule=obj_key_rule
                )

                if obj_ and obj_.get("was_enrich") and (
                        not obj_.get("was_convert")
                ):
                    obj_id = obj_key_rule.split(f"{key_rule}_")[-1]

                    transformation_data = await transformation_rule(
                        obj_data=obj_
                    )
                    await self._save_transformation_data(
                        model_=model_,
                        obj_id=obj_id,
                        transformation_data=transformation_data,
                    )
                    convert_count += self.CONCAT
                    logger.debug(
                        f"{key_rule}: id={obj_id}, enrich data was convert"
                    )

            logger.info(
                f"{key_rule}: enrich data was convert({convert_count} from "
                f"{len(scan_lst)})"
            )

    async def _get_object_data_by_key_rule(self, obj_key_rule: str) -> dict:
        if obj_data := await self.redis_storage.retrieve_state(
                key_=obj_key_rule
        ):
            obj_deserialize_data = json.loads(obj_data)

            return obj_deserialize_data

    async def _save_transformation_data(
        self, model_: BaseModel, obj_id: int, transformation_data: BaseSchema
    ) -> None:
        key_ = f"{model_.model_name()}_es_{obj_id}"

        await self.redis_storage.save_state(
            key_=key_, value=transformation_data.model_dump_json()
        )
