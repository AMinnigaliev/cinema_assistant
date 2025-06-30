from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core import nlp_config
from train_model import NLPModelTrainer


class NERModelScheduler:
    """Scheduler для обучения модели."""

    @classmethod
    def jobs(cls) -> list[dict[str, Any]]:
        """
        Задачи для обучения модели.

        @rtype: list[dict[str, Any]]
        @return:
        """
        return [
            {
                "cls_job": NLPModelTrainer,
                "job_params": {
                    "trigger": nlp_config.ner_task_trigger,
                    "days": nlp_config.ner_task_interval_days,
                    "coalesce": True,
                    "max_instances": 1,
                    "misfire_grace_time": None,
                },
            },
        ]

    @classmethod
    async def run(cls) -> None:
        scheduler_ = AsyncIOScheduler()

        for job_ in cls.jobs():
            scheduler_.add_job(
                func=job_["cls_job"]().run,
                **job_["job_params"],
            )
            scheduler_.start()
