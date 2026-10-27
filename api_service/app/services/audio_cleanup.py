import asyncio
import logging.config
import time
from pathlib import Path

from app.core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

RETENTION_HOURS = 24
CLEANUP_INTERVAL_SECONDS = 3600


def cleanup_old_audio(
    directory: Path,
    retention_hours: int = RETENTION_HOURS,
) -> int:
    """Удаляет MP3-файлы старше установленного срока хранения."""
    if not directory.is_dir():
        logger.warning("Каталог аудио не найден: %s", directory)
        return 0

    cutoff = time.time() - retention_hours * 3600
    deleted = 0

    for path in directory.glob("*.mp3"):
        try:
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink()
                deleted += 1
                logger.info("Удалён старый аудиофайл: %s", path.name)
        except OSError:
            logger.exception("Не удалось удалить аудиофайл: %s", path)

    logger.info("Очистка аудио завершена. Удалено файлов: %s", deleted)
    return deleted


async def run_audio_cleanup(directory: Path) -> None:
    """Периодически очищает каталог выходных аудиофайлов."""
    while True:
        try:
            await asyncio.to_thread(cleanup_old_audio, directory)
        except Exception:
            logger.exception("Ошибка во время очистки аудиофайлов")

        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
