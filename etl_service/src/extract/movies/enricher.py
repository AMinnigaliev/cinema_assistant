import json

from core.logger import logger
from extract.movies.enrich_rules import FilmWorkRules, PersonRules
from interface import ESClient_T, RedisStorage_T
from models.movies.pg_models import Base as BaseModel
from models.movies.pg_models import FilmWork, Person
from schemas import Base as BaseSchema
from utils.movies_utils.etl_enum import RuleTypes


class Enricher:
    """
    Класс по обогащению базовых сущностей сущностями-связками (их объединение).
    """

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
            FilmWork: {
                RuleTypes.SELECTION_RULE.value:
                    FilmWorkRules.film_work_selection_data_rule,
                RuleTypes.ENRICH_RULE.value:
                    FilmWorkRules.film_work_normalized_enrich_data_rule,
            },
            Person: {
                RuleTypes.SELECTION_RULE.value:
                    PersonRules.person_selection_data_rule,
                RuleTypes.ENRICH_RULE.value:
                    PersonRules.person_normalized_enrich_data_rule,
            },
        }

    @staticmethod
    def get_key_of_rule(model_: BaseModel) -> str:
        return model_.model_name()

    async def run(self) -> None:
        """
        Точка запуска. Этапы:
        - Получение правил для выборки и нормализации сущностей-связок по
        базовой модели из DB.
        - Получение из Storage базовые сущности.
        - Выборка и нормализация сущностей-связок из DB.
        - Связка базовой сущности с сущностями-связками.
        - Сохранение данных в Storage.

        :return None:
        """
        for model_, rules in self.model_rules.items():
            enrich_count = 0
            selection_rule, enrich_rule = (
                rules[RuleTypes.SELECTION_RULE.value],
                rules[RuleTypes.ENRICH_RULE.value],
            )

            key_rule = self.get_key_of_rule(model_=model_)
            scan_lst = await self.redis_storage.scan_iter(f"{key_rule}_*")

            if scan_lst:
                logger.info(
                    f"{key_rule}: start enrich(count: {len(scan_lst)})"
                )

            for obj_key_rule in scan_lst:
                obj_ = await self._get_object_data_by_key_rule(
                    obj_key_rule=obj_key_rule
                )

                if obj_ and not obj_.get("was_enrich") and not obj_.get(
                        "was_convert"
                ):
                    obj_id = obj_key_rule.split(f"{key_rule}_")[-1]

                    selection_data = await selection_rule(
                        pg_session=self.pg_session, obj_id=obj_id
                    )
                    enriched_data = await enrich_rule(
                        obj_data=obj_, selection_data=selection_data
                    )

                    await self._save_enrich_data(
                        obj_key_rule=obj_key_rule, enriched_data=enriched_data
                    )
                    enrich_count += self.CONCAT
                    logger.debug(f"{key_rule}: id={obj_id} was enrich")

            logger.info(
                f"{key_rule}: was enrich({enrich_count} from {len(scan_lst)})"
            )

    async def _get_object_data_by_key_rule(self, obj_key_rule: str) -> dict:
        if obj_data := await self.redis_storage.retrieve_state(
                key_=obj_key_rule
        ):
            obj_deserialize_data = json.loads(obj_data)

            return obj_deserialize_data

    async def _save_enrich_data(
            self, obj_key_rule: str, enriched_data: BaseSchema
    ):
        await self.redis_storage.save_state(
            key_=obj_key_rule, value=enriched_data.model_dump_json()
        )
