from django.urls import include, path
from rest_framework import routers

from .views.recipe_views import IngredientViewSet, RecipeViewSet, TagViewSet
from .views.user_views import CustomUserViewSet

router_v1 = routers.DefaultRouter()

router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
