from api.paginator import LimitPageNumberPagination
from api.serializers import SubscriptionSerializer, SubscriptionUserSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .serializers import AvatarSerializer

CustomUser = get_user_model()


class CustomUserViewSet(UserViewSet):

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions',
    )
    def list_subscriptions(self, request):
        user = request.user
        subs = CustomUser.objects.filter(subscription__user=user)
        paginator = LimitPageNumberPagination()
        result = paginator.paginate_queryset(subs, request)
        serializer = SubscriptionUserSerializer(
            result,
            many=True,
            context={'request': request},
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe',
    )
    def add_subscription(self, request, id):
        target_user = get_object_or_404(CustomUser, id=id)
        return self._create_subscription(request, target_user)

    @add_subscription.mapping.delete
    def remove_subscription(self, request, id):
        target_user = get_object_or_404(CustomUser, id=id)
        return self._delete_subscription(request, target_user)

    def _create_subscription(self, request, target_user):
        sub_serializer = SubscriptionSerializer(
            data={'user': request.user.id, 'subscription': target_user.id},
            context={'request': request}
        )
        sub_serializer.is_valid(raise_exception=True)
        sub_serializer.save()
        return Response(
            SubscriptionUserSerializer(
                target_user,
                context={'request': request},
            ).data,
            status=status.HTTP_201_CREATED
        )

    def _delete_subscription(self, request, target_user):
        user = request.user
        deleted, _ = Subscription.objects.filter(
            user=user,
            subscription=target_user,
        ).delete()

        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'Не найдена подписка'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(methods=['put'], detail=False, url_path='me/avatar')
    def update_avatar(self, request):
        avatar_data = self._handle_avatar(request.data)
        return Response(avatar_data.data)

    @update_avatar.mapping.delete
    def remove_avatar(self, request):
        user_instance = self._get_user_instance()
        user_instance.avatar.delete()
        user_instance.avatar = None
        user_instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _handle_avatar(self, data):
        user_instance = self._get_user_instance()
        avatar_serializer = AvatarSerializer(user_instance, data=data)
        avatar_serializer.is_valid(raise_exception=True)
        avatar_serializer.save()
        return avatar_serializer

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
            return [perm() for perm in self.permission_classes]
        return super().get_permissions()

    def _get_user_instance(self):
        return self.request.user
