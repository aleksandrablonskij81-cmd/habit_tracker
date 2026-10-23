from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Habit(models.Model):
    """Полезная или приятная привычка"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь'
    )
    place = models.CharField(max_length=200, verbose_name='Место')
    time = models.TimeField(verbose_name='Время')
    action = models.CharField(max_length=200, verbose_name='Действие')
    is_pleasant = models.BooleanField(default=False, verbose_name='Приятная привычка')
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_to',
        verbose_name='Связанная привычка'
    )
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name='Периодичность (дни)'
    )
    reward = models.CharField(max_length=200, blank=True, verbose_name='Вознаграждение')
    duration = models.PositiveIntegerField(
        default=60,
        verbose_name='Время на выполнение (сек)'
    )
    is_public = models.BooleanField(default=False, verbose_name='Публичная')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} в {self.time} в {self.place}'

    def clean(self):
        """Валидаторы"""
        # 1. Нельзя одновременно reward и related_habit
        if self.reward and self.related_habit:
            raise ValidationError('Нельзя одновременно указывать вознаграждение и связанную привычку.')

        # 2. Время выполнения ≤ 120 секунд
        if self.duration > 120:
            raise ValidationError('Время выполнения не может быть больше 120 секунд.')

        # 3. В связанные привычки — только приятные
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError('Связанная привычка должна быть приятной.')

        # 4. У приятной привычки нет reward и related_habit
        if self.is_pleasant:
            if self.reward:
                raise ValidationError('У приятной привычки не может быть вознаграждения.')
            if self.related_habit:
                raise ValidationError('У приятной привычки не может быть связанной привычки.')

        # 5. Периодичность не реже 1 раза в 7 дней
        if self.periodicity < 1 or self.periodicity > 7:
            raise ValidationError('Периодичность должна быть от 1 до 7 дней.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
