from django.contrib.auth import get_user_model
from recipes.serializers import ShortRecipeInfoSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscription
from users.serializers import UserSerializer

User = get_user_model()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'subscription')
        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscription'),
                message='Такая подписка уже есть.'
            ),
        )

    def validate(self, validated_data):
        current_user = self.context['request'].user
        target_user = validated_data['subscription']
        if current_user == target_user:
            raise serializers.ValidationError(
                'Ошибка. Подписка на себя.'
            )
        return validated_data


class SubscriptionUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, user_instance):
        request = self.context.get('request')
        limit = int(request.query_params.get('recipes_limit', 0))
        recipes_queryset = user_instance.recipes.all()
        if limit:
            recipes_queryset = recipes_queryset[:limit]
        return ShortRecipeInfoSerializer(recipes_queryset, many=True).data

    def get_recipes_count(self, user_instance):
        return user_instance.recipes.count()
