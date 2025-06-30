import json
from datetime import datetime

from core import logger
from database import clickhouse_session
from models.clickhouse_models import NERTrainingData


def get_train_dataset() -> list:
    with clickhouse_session.context_session() as clickhouse_session_:
        datetime_t = datetime.today().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        datetime_format = "%Y-%m-%d %H:%M:%S"
        datetime_str = datetime.strftime(datetime_t, datetime_format)

        ner_trainings_data = clickhouse_session_.select(
            query=(
                f"SELECT * FROM nertrainingdata "
                f"WHERE nertrainingdata.timestamp >= '{datetime_str}' "
                f"AND nertrainingdata.status = 'approved'"
            ),
            model_class=NERTrainingData,
        )

        train_dataset = list()
        for ner_training_data in ner_trainings_data:
            if t_data := json.loads(ner_training_data.training_data):
                try:
                    ent = t_data["entities"]
                    train_dataset.append(
                        (
                            t_data["promt"],
                            {
                                "entities": [
                                    (ent["start"], ent["stop"], ent["type"]),
                                ],
                            },
                        )
                    )

                except KeyError as ex:
                    logger.warning(f"Error get data for train dataset: {ex}")

        return train_dataset
