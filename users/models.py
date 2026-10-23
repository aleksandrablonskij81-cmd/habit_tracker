from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Профиль пользователя с Telegram chat_id"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    telegram_chat_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Telegram Chat ID'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'{self.user.username} — {self.telegram_chat_id or "не указан"}'
