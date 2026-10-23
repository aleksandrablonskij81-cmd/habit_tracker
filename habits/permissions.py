from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Редактировать/удалять может только владелец."""

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Редактирование/удаление — только владельцу
        return obj.user == request.user