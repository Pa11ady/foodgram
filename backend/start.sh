#!/bin/bash

# Удаление базы данных db.sqlite3
if [ -f "db.sqlite3" ]; then
    echo "Removing existing database db.sqlite3..."
    rm db.sqlite3
else
    echo "Database db.sqlite3 not found, skipping removal..."
fi

# Применение миграций
echo "Applying migrations..."
#python manage.py makemigrations
python manage.py migrate


echo "Creating basic tags..."
echo "Loading ingredients..."
python manage.py load_data

# Запуск сервера
echo "Starting Django development server..."
python manage.py runserver