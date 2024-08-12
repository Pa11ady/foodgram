import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag

DATA_ROOT = os.path.join(settings.BASE_DIR, "data/ingredients.csv")


def load_ingredients_from_csv(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        file_reader = csv.reader(file)
        return [
            Ingredient(name=row[0], measurement_unit=row[1])
            for row in file_reader
        ]


def create_default_tags():
    tags = {
        'bre': 'Завтрак',
        'din': 'Обед',
        'sup': 'Ужин',
    }

    tags_to_create = [
        Tag(name=name, slug=slug)
        for slug, name in tags.items()
        if not Tag.objects.filter(slug=slug).exists()
    ]

    Tag.objects.bulk_create(tags_to_create)
    return tags_to_create


class Command(BaseCommand):
    help = 'Загрузка ингредиентов и создание  тегов.'

    def handle(self, *args, **kwargs):
        ingredients = load_ingredients_from_csv(DATA_ROOT)
        Ingredient.objects.bulk_create(ingredients)
        self.stdout.write(self.style.SUCCESS(
            "Ингредиенты загружены в БД."))

        created_tags = create_default_tags()
        self.stdout.write(self.style.SUCCESS(f'Созданы теги: {created_tags}'))
