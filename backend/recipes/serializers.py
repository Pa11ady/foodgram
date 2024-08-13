from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from users.serializers import Base64ImageField, UserSerializer

from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='name.id')
    name = serializers.ReadOnlyField(source='name.name')
    measurement_unit = serializers.ReadOnlyField(
        source='name.measurement_unit',)

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(many=True,
                                              source='recipeingredients',)
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(read_only=True,
                                                   default=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time',)


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientsSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name', 'image', 'text',
                  'cooking_time')

    def _check_required_fields(self, data):
        required_fields = ['tags', 'ingredients', 'name', 'text',
                           'cooking_time']
        missing_fields = [field for field in required_fields if
                          not data.get(field)]
        if missing_fields:
            error_message = {
                field: f'Поле {field} обязательно для создания рецепта.' for
                field in missing_fields}
            raise ValidationError(error_message)

    def _validate_unique_tags(self, tags):
        duplicates = [tag for tag in tags if tags.count(tag) > 1]
        if duplicates:
            raise ValidationError({'tags': 'Теги не должны повторяться.'})

    def _validate_ingredients_list(self, ingredients):
        ingredient_ids = [ingredient.get('name', {}).get('id') for ingredient
                          in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError({'ingredients': 'Нужны разные ингредиенты.'})

    def validate(self, data):
        self._check_required_fields(data)
        self._validate_unique_tags(data['tags'])
        self._validate_ingredients_list(data['ingredients'])
        return data

    def validate_image(self, value):
        if not value:
            raise ValidationError('Поле image обязательно.')
        return value

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data

    def _prepare_ingredients(self, recipe, ingredients_data):
        ingredient_instances = [
            RecipeIngredients(
                recipe_name=recipe,
                name=ingredient.pop('name')['id'],
                **ingredient
            )
            for ingredient in ingredients_data
        ]
        return ingredient_instances

    def _save_recipe_with_ingredients_and_tags(self, recipe, ingredients_data,
                                               tags):
        recipe.tags.set(tags)
        RecipeIngredients.objects.bulk_create(ingredients_data)

    def _create_recipe(self, data):
        return Recipe.objects.create(**data,
                                     author=self.context['request'].user,)

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe_instance = self._create_recipe(validated_data)
        ingredient_instances = self._prepare_ingredients(recipe_instance,
                                                         ingredients_data)
        self._save_recipe_with_ingredients_and_tags(recipe_instance,
                                                    ingredient_instances, tags)

        return recipe_instance

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance.ingredients.clear()
        instance.tags.clear()

        ingredient_instances = self._prepare_ingredients(instance,
                                                         ingredients_data)
        self._save_recipe_with_ingredients_and_tags(instance,
                                                    ingredient_instances, tags)

        return super().update(instance, validated_data)


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(queryset=ShoppingCart.objects.all(),
                                    fields=['user', 'recipe'],
                                    message='Рецепт уже в списке покупок.')
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        self._check_recipe_is_favorited(user, recipe)
        return data

    def _check_recipe_is_favorited(self, user, recipe):
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в избранном.')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class ShortRecipeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
