#!/bin/bash

set -e

if [ ! -f /app/.init_done ]; then
    echo "Создание схемы auth в postgres..."
    python3 /app/src/app_init/create_schemas.py || { echo "Ошибка при выполнении create_schemas.py"; exit 1; }

    echo "Применение миграций..."
    alembic upgrade head

    echo "Создание схемы auth в postgres..."
    python3 /app/src/app_init/create_partitions.py || { echo "Ошибка при выполнении create_partitions.py"; exit 1; }

    echo "Создание суперпользователя..."
    python3 /app/src/app_init/create_superuser.py || { echo "Ошибка при выполнении create_superuser.py"; exit 1; }

    echo "Предварительные операции успешно выполнены."

    touch /app/.init_done

fi

echo "Запуск приложения..."
exec uvicorn src.main:app --host 0.0.0.0 --port "$AUTH_SERVICE_PORT"