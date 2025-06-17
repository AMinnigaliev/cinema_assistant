import socket
from datetime import datetime

from sqlalchemy import select

from core.logger import logger
from extract.movies.producer_rules import (FilmWorkRules, GenreRules,
                                           PersonRules)
from interface import ESClient_T, RedisStorage_T, check_free_size_storage
from models.movies.pg_models import (BaseWithTimeStampedType, FilmWork, Genre,
                                     Person)
from schemas import Base as BaseSchema
from utils import EntitiesNotFoundInDBError, backoff_by_connection
from utils.movies_utils.etl_enum import RuleTypes


class Producer:
    """Класс по получению данных базовых сущностей из DB."""

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

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
                RuleTypes.NORMALIZE_RULE.value:
                    FilmWorkRules.film_work_normalize_data_rule,
            },
            Person: {
                RuleTypes.SELECTION_RULE.value:
                    PersonRules.person_selection_data_rule,
                RuleTypes.NORMALIZE_RULE.value:
                    PersonRules.person_normalize_data_rule,
            },
            Genre: {
                RuleTypes.SELECTION_RULE.value:
                    GenreRules.genre_selection_data_rule,
                RuleTypes.NORMALIZE_RULE.value:
                    GenreRules.genre_normalize_data_rule,
            },
        }

    @staticmethod
    def get_key_of_rule(model_: BaseWithTimeStampedType) -> str:
        return model_.model_name()

    def str_to_datetime(self, datetime_str: str) -> datetime:
        return datetime.strptime(datetime_str, self.DATETIME_FORMAT)

    def datetime_to_str(self, datetime_: datetime) -> str:
        return datetime.strftime(datetime_, self.DATETIME_FORMAT)

    async def run(self) -> None:
        """
        Точка запуска. Этапы:
        - Получение правил для выборки и нормализации данных по модели из DB.
        - Получение date_modified.
        - Выборка и нормализация данных из DB.
        - Сохранение данных в Storage.
        - Обновление date_modified для модели DB.

        :return None:
        """
        for model_, rules in self.model_rules.items():
            selection_rule = rules[RuleTypes.SELECTION_RULE.value]
            normalize_rule = rules[RuleTypes.NORMALIZE_RULE.value]

            try:
                date_modified = await self._get_date_modified(model_=model_)

            except EntitiesNotFoundInDBError as ex:
                logger.warning(f"{ex} (model was skip)")
                continue

            if selection_data := await selection_rule(
                pg_session=self.pg_session, date_modified=date_modified
            ):
                logger.info(
                    f"{model_.model_name()}, received date modified: "
                    f"{date_modified}"
                )

                normalized_data = normalize_rule(selection_data=selection_data)
                logger.debug(
                    f"{model_.model_name()}, select and normalize data for "
                    f"date modified: {date_modified}"
                )

                await self._insert_data_in_storage(
                    model_=model_, normalized_data=normalized_data
                )
                await self._update_date_modified(
                    model_=model_, selection_data=selection_data
                )

                logger.info(
                    f"{model_.model_name()}, ids({len(selection_data)})="
                    f"{[d.id for d in selection_data]} was produce"
                )

            else:
                logger.info(
                    f"{model_.model_name()}, not found data for modified"
                )

    async def _get_date_modified(
            self, model_: BaseWithTimeStampedType
    ) -> datetime:
        """
        Получение modified по модели из DB. Если данной информации по модели
        нет в Storage, получаем ее из DB и записываем в Storage.

        :param BaseWithTimeStampedType model_:
        :return datetime date_modified:
        """
        key_rule = self.get_key_of_rule(model_=model_)

        if date_from_storage := await self.redis_storage.get_(name=key_rule):
            date_modified = self.str_to_datetime(
                datetime_str=date_from_storage
            )

        else:
            date_modified = await self._get_date_modified_from_db(
                model_=model_
            )
            await self._set_date_modified(
                key_rule=key_rule, date_modified=date_modified
            )

        return date_modified

    @backoff_by_connection(
        exceptions=(ConnectionRefusedError, socket.gaierror)
    )
    async def _get_date_modified_from_db(
        self, model_: BaseWithTimeStampedType
    ) -> datetime:
        query_ = await self.pg_session.execute(
            select(model_).order_by(model_.modified.asc())
        )
        last_modified_entity = query_.scalar()

        if not last_modified_entity:
            raise EntitiesNotFoundInDBError(message=(
                f"not found records in DB for model '{model_.model_name()}'"
            ))

        return last_modified_entity.modified

    async def _update_date_modified(
        self, model_: BaseWithTimeStampedType, selection_data: list[BaseSchema]
    ) -> None:
        ord_selection_data = sorted(
            selection_data, key=lambda d: d.modified, reverse=False
        )

        date_modified = ord_selection_data[-1].modified
        key_rule = self.get_key_of_rule(model_=model_)
        await self._set_date_modified(
            key_rule=key_rule, date_modified=date_modified
        )

        logger.debug(
            f"{model_.model_name()}: set new date modified({date_modified})"
        )

    async def _set_date_modified(
            self, key_rule: str, date_modified: datetime
    ) -> None:
        await self.redis_storage.set_(
            name=key_rule, value=self.datetime_to_str(datetime_=date_modified)
        )

    @check_free_size_storage()
    async def _insert_data_in_storage(
        self,
        model_: BaseWithTimeStampedType,
        normalized_data: list[BaseSchema],
    ) -> None:
        key_rule = self.get_key_of_rule(model_=model_)

        for data_ in normalized_data:
            key_ = "{}_{}".format(key_rule, data_.id)
            await self.redis_storage.save_state(
                key_=key_, value=data_.model_dump_json()
            )

        logger.debug(
            f"{model_.model_name()}: normalized data was insert in storage"
        )
