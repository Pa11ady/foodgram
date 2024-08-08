from django.contrib.auth import validators
from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LEN = 30


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(unique=True, max_length=130,
                              verbose_name='Почта')
    username = models.CharField(max_length=100, unique=True,
                                verbose_name='Пользователь',
                                validators=[
                                    validators.UnicodeUsernameValidator()])
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='images/avatars/', null=True,
                               default=None)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:MAX_LEN]


class Subscription(models.Model):
    subscription = models.ForeignKey(CustomUser, related_name='subscription',
                                     verbose_name='Подписка',
                                     on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='follower',
                             verbose_name='Подписчик',
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(fields=['user', 'subscription'],
                                               name='unique_subscription')]

    def __str__(self):
        return (
            f'{self.user[:MAX_LEN]} на '
            f'на {self.subscription[:MAX_LEN]}'
        )
