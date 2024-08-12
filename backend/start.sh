#!/bin/bash

if [ -f "db.sqlite3" ]; then
    echo "Удаление существующей базы данных db.sqlite3..."
    rm db.sqlite3
else
    echo "База данных db.sqlite3 не найдена, пропускаем удаление..."
fi

echo "Применение миграций..."
python manage.py makemigrations
python manage.py migrate

echo "Создание базовых тегов..."
echo "Загрузка ингредиентов..."
python manage.py load_data

echo "Создание суперпользователя..."
python manage.py create_superuser

echo "Запуск сервера разработки Django..."
python manage.py runserver
