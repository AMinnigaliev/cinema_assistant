# Проект "Ассистент кинотеатра"

**Цель работы** - реализовать интеграцию между сервисом поиска фильмов и голосовым помощником.

* * *

🔹 **Запуск проекта (запуск в текущей директории):**
```sh
docker compose up -d
```

* * *

🔹 **Запуск тестов (запуск в директории 'tests'):**
```sh
docker compose -f ./docker-compose-apps.yaml -f ./docker-compose-services.yaml -f ./docker-compose-tests.yaml up -d
```
🔹 **Запуск тестов с открытыми портами сервисов (запуск в директории 'tests'):**
```sh
docker compose -f ./docker-compose-apps.yaml -f ./docker-compose.override.yaml -f ./docker-compose-services.yaml -f ./docker-compose-tests.yaml up -d
```
🔹 **Запуск сервисов с открытыми портами для написания тестов (запуск в директории 'tests'):**
```sh
docker compose -f ./docker-compose-apps.yaml -f ./docker-compose-services.yaml -f ./docker-compose.override.yaml up -d
```

* * *

## Стек технологий
- Python 3.12;
- Контейнеризация:
  - **Docker**(https://docs.docker.com/);
- Web Servers:
  - **Uvicorn**(https://www.uvicorn.org/);
  - **Nginx**(https://nginx.org/en/docs/);
- Rest-Frameworks:
  - **Fast API**(https://fastapi.tiangolo.com/);
- SearchEngine / DataBase:
  - **Elasticsearch**(https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html);
  - **RedisCluster**(https://redis-py.readthedocs.io/en/stable/index.html);
  - **PostgreSQL**(**SQLAlchemyORM**: https://docs.sqlalchemy.org/en/20/orm/);
- DataModels:
  - **Pydantic**(https://docs.pydantic.dev/latest/);

## Архитектура проекта
### Основные модули проекта:
- Сервис кинотеатра (сервис выдачи контента);
- ETL-сервис;
- Auth-сервис;
- Movies-сервис;
- API gateway;
- Voice-сервис;

Схема архитектуры проекта:
![scheme](docs/project/project_scheme.png)

## Основные модели Postgres
- FilmWork: Фильм;
- Genre: Жанр;
- GenreFilmWork: связь Жанра с Фильмом;
- Person: Персона;
- PersonFilmWork: связь Персоны с Фильмом;
- User: Пользователь;
- LoginHistory: история авторизации пользователя;
- SocialAccount.

Cхемы БД:
![scheme](docs/postgres/postgres_auth.png)
![scheme](docs/postgres/postgres_content.png)

## Схема индексов Elasticsearch
![scheme](docs/elastic/elastic_index.png)

* * *

# Соглашения разработки:
## GitFlow
### Ветки (branches):
- **main**: основная(работоспособная) ветка кода, содержащая код для отправки на ревью.
- **develop**: рабочая ветка, содержащая актуальную кодовую базу для разработки.

### Работа с ветками:
- Разработка нового функционала: branch: develop -> feature/....
- Исправление ошибки в новом функционале: branch: develop(main) -> fix/...

## REST-URI:
### Версионирование:
- Поддержка **Stripe**-подхода (https://docs.stripe.com/api/versioning)

### Шаблоны построения WebSocket‑событий:
TODO: добавить

## Code Style:
- **PEP8**(https://peps.python.org/pep-0008/), необходимо соблюдать;
- Docstring-формат - **Epytext**(https://epydoc.sourceforge.net/manual-epytext.html), желательно соблюдать;
- Linters: **Flake8**(https://flake8.pycqa.org/en/latest/) или любой другой не конфликтующий, желательно соблюдать;
- **Pre-commit**(https://pre-commit.com/), желательно использовать;
