import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cоздание супер админа'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS('Админ уже существует.'))
            return

        user_data = {
            'email': os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin_s@admin.com'),
            'username': os.getenv('DJANGO_SUPERUSER_USERNAME', 'name_ad'),
            'first_name': os.getenv('DJANGO_SUPERUSER_FIRST_NAME', 'first_ad'),
            'last_name': os.getenv('DJANGO_SUPERUSER_LAST_NAME', 'last_ad'),
            'password': os.getenv('DJANGO_SUPERUSER_PASSWORD', 'super')
        }

        User.objects.create_superuser(**user_data)
        self.stdout.write(self.style.SUCCESS(
            f'Админ {user_data["username"]} создан.'))
