from elasticsearch import AsyncElasticsearch

from settings import config


def make_async_es_client() -> AsyncElasticsearch:
    """
    Асинхронный клиент Elasticsearch для тестов и утилит.
    """
    return AsyncElasticsearch(
        hosts=[
            f"{config.elastic_schema}://{config.elastic_host}:"
            f"{config.elastic_port}"
        ],
        basic_auth=(config.elastic_name, config.elastic_password),
        request_timeout=config.request_timeout,
    )
