from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import Subscription
from ..fields import Base64ImageField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )
        if not user:
            return False
        return Subscription.objects.filter(user=user,
                                           subscription=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
