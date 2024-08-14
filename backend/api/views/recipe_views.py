from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)

from ..filters import IngredientFilter, RecipeFilter
from ..paginator import LimitPageNumberPagination
from ..permissions import IsAuthorOrReadOnly
from ..serializers.recipe_serializers import (FavoriteSerializer,
                                              IngredientSerializer,
                                              RecipeReadSerializer,
                                              RecipeWriteSerializer,
                                              ShoppingCartSerializer,
                                              ShortRecipeInfoSerializer,
                                              TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        recipes = super().get_queryset()
        if user.is_authenticated:
            recipes = recipes.with_user_annotations(user)
        return recipes

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True, methods=['post'], url_path='shopping_cart')
    def add_to_shopping_cart(self, request, pk=None):
        return self._handle_favorite_or_cart_action(
            request=request, pk=pk, model=ShoppingCart,
            serializer_class=ShoppingCartSerializer, action='create')

    @add_to_shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        return self._handle_favorite_or_cart_action(
            request=request, pk=pk, model=ShoppingCart, action='delete')

    @action(detail=True, methods=['post'], url_path='favorite')
    def add_to_favorite(self, request, pk=None):
        return self._handle_favorite_or_cart_action(
            request=request, pk=pk, model=Favorite,
            serializer_class=FavoriteSerializer, action='create')

    @add_to_favorite.mapping.delete
    def remove_from_favorite(self, request, pk=None):
        return self._handle_favorite_or_cart_action(
            request=request, pk=pk, model=Favorite,
            action='delete')

    def _handle_favorite_or_cart_action(self, request, pk, model,
                                        serializer_class=None,
                                        action='create'):
        recipe = get_object_or_404(Recipe, pk=pk)

        if action == 'create':
            data = {'user': request.user.id, 'recipe': recipe.id}
            serializer = serializer_class(data=data,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                ShortRecipeInfoSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        elif action == 'delete':
            deleted, _ = model.objects.filter(user=request.user,
                                              recipe=recipe).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Recipe not found in the list.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _create_shopping_txt(self, ingredients):
        shopping_list = [
            (f"{ingredient['name__name']}: "
             f"{ingredient['total_amount']} "
             f"{ingredient['name__measurement_unit']}\n")
            for ingredient in ingredients
        ]
        return '\n'.join(shopping_list) + '\n'

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredients.objects.filter(
            recipe_name__shoppingcart__user=request.user
        ).values(
            'name__name', 'name__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        )
        shopping_list = self._create_shopping_txt(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')
