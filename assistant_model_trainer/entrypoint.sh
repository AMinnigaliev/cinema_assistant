#!/bin/sh
set -e

echo "🟡 Миграция схемы ClickHouse..."
python3 /app/database/clickhouse_migration/migrate.py

echo "🟡 Инициализация датасета..."
python3 /app/app_init/clickhouse_init_dataset.py

echo "🚀 Запуск приложения..."
python3 /app/run.py
