import json
from datetime import datetime

from core import logger, nlp_config
from database import clickhouse_session
from models.clickhouse_models import NERTrainingData


def init_dataset() -> None:
    with clickhouse_session.context_session() as clickhouse_session_:
        datetime_t = datetime.today().replace(hour=0, minute=0, second=0)
        datetime_str = datetime.strftime(datetime_t, "%Y-%m-%d %H:%M:%S")

        insert_data = list()
        with open(f"{nlp_config.base_dir}/app_init/init_dataset.json", "r") as fp:
            for dataset in json.load(fp):
                insert_data.append(
                    NERTrainingData(
                        request_id="init",
                        status="approved",
                        training_data=json.dumps(dataset, ensure_ascii=False),
                        timestamp=datetime_str,
                    )
                )

            try:
                clickhouse_session_.insert(insert_data)

            except Exception as ex:
                logger.error(f"Error insert init dataset in clickhouse: {ex}")


if __name__ == "__main__":
    init_dataset()
