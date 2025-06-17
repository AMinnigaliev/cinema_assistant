import json
import os

from core import config
from core.logger import logger
from interface import RedisStorage_T
from interface.es_client import ESClient_T
from models.movies.pg_models import Base as BaseModel
from models.movies.pg_models import FilmWork, Genre, Person
from schemas.movies_schemas.film_work_models import FilmWorkESModel
from schemas.movies_schemas.genre_models import GenreModel
from schemas.movies_schemas.person_models import PersonModel


class Loader:
    """Класс по загрузке данных в ES."""

    MODELS_PATH = "models"
    MOVIES_MODELS_PATH = "movies"
    ES_INDICES_PATH = "es_indices"
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
    def models(self) -> dict:
        return {
            FilmWork: FilmWorkESModel,
            Person: PersonModel,
            Genre: GenreModel,
        }

    @staticmethod
    def get_key_of_rule(model_: BaseModel) -> str:
        return model_.model_name()

    @staticmethod
    def _get_clear_es_dict(es_model_dict: dict) -> dict:
        es_model_dict.pop("was_enrich", None)
        es_model_dict.pop("was_convert", None)

        return es_model_dict

    async def run(self) -> None:
        """
        Точка запуска. Этапы:
        - Получение из Storage сущности.
        - Проверяем сущность на валидность pydantic-модели.
        - Очистка и сериализация сущности.
        - Сохранение данных в ES.
        - Очистка Storage.

        :return None:
        """
        for model_, es_model_cls in self.models.items():
            load_count = 0
            key_rule = self.get_key_of_rule(model_=model_)

            await self._es_client.create_index_with_ignore(
                index_=key_rule, body=self._get_es_schema(name=key_rule)
            )
            scan_lst = await self.redis_storage.scan_iter(f"{key_rule}_es_*")

            if scan_lst:
                logger.debug(
                    f"{key_rule}: start load to ES(count: {len(scan_lst)})"
                )

            for obj_key_rule in scan_lst:
                obj_id = obj_key_rule.split(f"{key_rule}_es_")[-1]
                obj_ = await self._get_object_data_by_key_rule(
                    obj_key_rule=obj_key_rule
                )

                es_model_dict = es_model_cls(**obj_).model_dump(mode="json")

                if (
                    es_model_dict
                    and es_model_dict.get("was_enrich")
                    and es_model_dict.get("was_convert")
                ):
                    result_ = await self._es_client.insert_document(
                        index_=key_rule,
                        document=self._get_clear_es_dict(
                            es_model_dict=es_model_dict
                        ),
                        id_=obj_id,
                    )

                    if result_.get("status") is False:
                        logger.error(
                            f"{key_rule}: error insert data(id={obj_id}) in "
                            f"ES: {result_.get('message')}"
                        )
                    else:
                        load_count += self.CONCAT
                        logger.debug(
                            f"{key_rule}: id={obj_id}, data was save in ES"
                        )

                        await self._delete_objects_by_obj_id(
                            obj_id=obj_id, key_rule=key_rule
                        )

            logger.info(
                f"{key_rule}: was load in ES({load_count} from "
                f"{len(scan_lst)})"
            )

    async def _get_object_data_by_key_rule(self, obj_key_rule: str) -> dict:
        obj_data = await self.redis_storage.retrieve_state(key_=obj_key_rule)
        obj_deserialize_data = json.loads(obj_data)

        return obj_deserialize_data

    async def _delete_objects_by_obj_id(
            self, obj_id: str, key_rule: str
    ) -> None:
        """
        Удаление объектов из Storage:
        - Удаление обогащенных сущностей.
        - Удаление сущностей, приведенных к нормали для сохранения в ES.

        :param str obj_id:
        :param str key_rule:
        :return None:
        """
        base_name = f"{key_rule}_{obj_id}"
        await self.redis_storage.delete_(name=base_name)
        logger.debug(
            f"{key_rule}: id={obj_id}, BASE data was delete from Storage"
            # nosec B608
        )

        es_name = f"{key_rule}_es_{obj_id}"
        await self.redis_storage.delete_(name=es_name)
        logger.debug(
            f"{key_rule}: id={obj_id}, ES data was delete from Storage"
            # nosec B608
        )

    def _get_es_schema(self, name: str):
        try:
            with open(
                os.path.join(
                    config.base_dir,
                    self.MODELS_PATH,
                    self.MOVIES_MODELS_PATH,
                    self.ES_INDICES_PATH,
                    f"{name}.json"
                ),
                "r",
            ) as fp:
                body_index = json.load(fp)

                return body_index

        except FileNotFoundError:
            logger.warning(
                f"{name}: not found json-file with index schema. If index not "
                f"exist, it was create auto"
            )
