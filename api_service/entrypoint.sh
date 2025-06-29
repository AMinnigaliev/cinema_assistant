#!/bin/bash

set -e

if [ ! -f /app/.init_done ]; then
    echo "Создание таблицы voice_assistant_request..."
    python3 /app/app/app_init/create_table.py || { echo "Ошибка при выполнении create_table.py"; exit 1; }

    echo "Предварительные операции успешно выполнены."

    touch /app/.init_done

fi

echo "Запуск приложения..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000