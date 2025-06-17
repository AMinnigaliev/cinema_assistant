from abc import ABC, abstractmethod


class ETLSchedulerInterface(ABC):
    """Интерфейс для реализации ETL-процессов через AsyncIOScheduler."""

    @classmethod
    @abstractmethod
    def jobs(cls) -> list[dict]:
        """
        Метод получения всех задач (с заданными параметрами) для планировщика.
        """

    @classmethod
    @abstractmethod
    async def run(cls) -> None:
        """Метод добавления всех задач в планировщике."""
