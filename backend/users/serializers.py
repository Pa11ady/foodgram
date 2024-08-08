import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import Subscription

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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_info, img_str = data.split(';base64,')
            file_ext = format_info.split('/')[-1]
            data = ContentFile(
                base64.b64decode(img_str),
                name=f'temp.{file_ext}'
            )
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
