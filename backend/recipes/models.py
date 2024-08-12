from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django.db.models import Exists, OuterRef

MAX_LEN = 40

User = get_user_model()


class Tag(models.Model):
    slug = models.SlugField(unique=True, max_length=50, verbose_name='Тег')
    name = models.CharField(unique=True, max_length=50, verbose_name='Тег')

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:MAX_LEN]


class Ingredient(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название')
    measurement_unit = models.CharField(max_length=50,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredient'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient')]

    def __str__(self):
        return self.name[:MAX_LEN]


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(to='Recipe', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Рецепт в покупках'
        verbose_name_plural = 'Рецепты в покупках'
        default_related_name = 'shoppingcart'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_recipe_user_cart')]

    def __str__(self):
        return (
            f'{self.recipe[:MAX_LEN]} добавлен в покупки '
            f'{self.user[:MAX_LEN]}'
        )


class Favorite(models.Model):
    recipe = models.ForeignKey(to='Recipe', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        default_related_name = 'favorite'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_recipe_user_favor')]

    def __str__(self):
        return f'{self.recipe[:MAX_LEN]} добавлен {self.user[:MAX_LEN]}'

class RecipeQuerySet(models.QuerySet):
    def with_user_annotations(self, user):
        return self.annotate(is_favorited=Exists(Favorite.objects.filter(
            recipe=OuterRef('id'), user=user)),
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                recipe=OuterRef('id'), user=user,)))


class Recipe(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название')
    image = models.ImageField(null=True, upload_to='recipes/images/',
                              default=None)
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления, мин.',
        validators=[
            MinValueValidator(limit_value=1,
                              message='Минимальное время 1 минута'),
            MaxValueValidator(limit_value=600,
                              message='Максимальное временя 600 минут')]
    )

    created_at = models.DateTimeField(verbose_name='Добавлено',
                                      auto_now_add=True)
    author = models.ForeignKey(to=User, verbose_name='Автор',
                               on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(blank=False, to=Ingredient,
                                         through='RecipeIngredients')
    tags = models.ManyToManyField(Tag)
    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name[:MAX_LEN]


class RecipeIngredients(models.Model):
    recipe_name = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)
    name = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(limit_value=1,
                              message='Минимальное кол-во 1'),
            MaxValueValidator(limit_value=1000,
                              message='Максимальное кол-во 1000')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        default_related_name = 'recipeingredients'
        constraints = [
            models.UniqueConstraint(fields=['recipe_name', 'name'],
                                    name='unique_ingredient_in_recipe'),]

    def __str__(self):
        return (
            f'{self.name[:MAX_LEN]} для '
            f'рецепта {self.recipe_name[:MAX_LEN]}'
        )
