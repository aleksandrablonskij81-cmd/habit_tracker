from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Habit"""

    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'place', 'time', 'action', 'is_pleasant',
            'related_habit', 'periodicity', 'reward', 'duration',
            'is_public', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']