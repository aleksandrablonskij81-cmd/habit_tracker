from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Habit
from .serializers import HabitSerializer
from .paginators import HabitPagination
from .permissions import IsOwnerOrReadOnly


class HabitViewSet(viewsets.ModelViewSet):
    """CRUD для привычек пользователя"""
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at', 'time']
    ordering = ['-created_at']

    def get_queryset(self):
        """Только свои привычки"""
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """При создании — назначаем владельца"""
        serializer.save(user=self.request.user)


class PublicHabitViewSet(viewsets.ReadOnlyModelViewSet):
    """Список публичных привычек (только чтение)"""
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)