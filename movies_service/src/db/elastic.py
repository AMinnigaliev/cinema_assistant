import logging

from elasticsearch import ApiError, AsyncElasticsearch, ConnectionError

from src.core.config import settings
from src.services.elastic_service import ElasticService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

es: ElasticService | None = None


async def get_elastic() -> ElasticService:
    global es
    # Проверка, существует ли es и активно ли соединение
    if not es or not await es.es_client.ping():
        logger.info("Создание клиента Elasticsearch...")
        es_client = None
        try:
            es_client = AsyncElasticsearch(
                hosts=[
                    f"{settings.elastic_scheme}://{settings.elastic_host}:"
                    f"{settings.elastic_port}"
                ],
                basic_auth=(settings.elastic_name, settings.elastic_password),
            )
            if not await es_client.ping():
                raise ConnectionError("Elasticsearch недоступен.")

            logger.info("Клиент Elasticsearch успешно создан.")

            es = ElasticService(es_client)

        except ConnectionError as ce:
            logger.error(f"Ошибка подключения к Elasticsearch: {ce}")
            if es_client:
                await es_client.close()
            raise
        except ApiError as ae:
            logger.error(f"Ошибка API Elasticsearch: {ae}")
            if es_client:
                await es_client.close()
            raise
        except Exception as e:
            logger.error(f"Ошибка при создании клиента Elasticsearch: {e}")
            if es_client:
                await es_client.close()
            raise

    return es


async def close_elastic():
    """
    Закрывает соединение с Elasticsearch.
    """
    global es
    if es:
        logger.info("Закрытие соединения с Elasticsearch...")
        await es.close()
        es = None
        logger.info("Соединение с Elasticsearch успешно закрыто.")
    else:
        logger.info("Соединение с Elasticsearch уже было закрыто.")
