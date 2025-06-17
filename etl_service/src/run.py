import asyncio

from scheduler import MoviesETLScheduler


if __name__ == "__main__":
    """
    Точка входа. Запуск планировщиков ETL-событий:
    - MoviesETLScheduler: ETL-обработчиков для сервиса Кинотеатр.
    - EventsETLScheduler: ETL-обработчиков для сервиса генерации контента
    пользователем (UGC).
    """
    current_loop = asyncio.get_event_loop()

    current_loop.run_until_complete(MoviesETLScheduler.run())

    current_loop.run_forever()
