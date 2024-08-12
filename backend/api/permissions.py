from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        is_safe = request.method in SAFE_METHODS
        is_author = obj.author == request.user
        return is_safe or is_author
