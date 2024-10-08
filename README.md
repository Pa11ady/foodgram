# Foodgram

[Сайт проекта](https://superf00d.ddns.net)

## Описание проекта

Foodgram — это сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
Также есть возможность скачивать список покупок.

## Возможности проекта

- Публикация рецептов.
- Добавление рецептов в избранное.
- Подписка на публикации других авторов.
- Создание списка продуктов для выбранных рецептов.
- Выгрузка списка покупок в текстовой файл.

## Основные страницы

- Главная
- Страница входа
- Страница регистрации
- Страница рецепта
- Страница пользователя
- Страница подписок
- Избранное
- Список покупок
- Создание и редактирование рецепта
- Страница смены пароля
- Статические страницы «О проекте» и «Технологии»

## Стек технологий

- Python
- Django
- Django REST Framework
- Docker
- Sqlite
- PostgreSQL
- Nginx
- gunicorn

## Локальное развертывание проекта

1. **Клонирование репозитория:**

    ```bash
    git clone git@github.com:Pa11ady/foodgram.git
    cd foodgram
    ```

2. **Заполнение файла .env:**

    Создать файл `.env` в корневой директории проекта по аналогии с .env.examle  


3. **Запуск всех контейнеров проекта:**

    Выполнить команду из корневой папки проекта:

    ```bash
    docker compose -f docker-compose.production.yml up
    ```

    Проект будет доступен по адресу `http://127.0.0.1:8080/`.
    Применение миграций и сбор статики призойдёт автоматом.

4. **Создание супер пользователя и загрузка данных:**

    ```bash
    docker compose -f docker-compose.production.yml exec backend  bash
    python manage.py createsuperuser
    python manage.py load_data
    ```
    


## Автор

**Воробьёв Павел**
