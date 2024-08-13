#!/bin/bash
echo "Создание базовых тегов..."
echo "Загрузка ингредиентов..."
python manage.py load_data

echo "Создание суперпользователя..."
python manage.py create_superuser
