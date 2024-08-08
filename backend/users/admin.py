from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name')
    search_fields = ('first_name', 'last_name')
    list_filter = ('username',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription')
    search_fields = ('user',)
    list_filter = ('subscription',)
