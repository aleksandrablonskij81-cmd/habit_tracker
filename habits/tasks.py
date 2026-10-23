from celery import shared_task
from django.conf import settings
import requests
from .models import Habit
from users.models import UserProfile


@shared_task
def send_habit_reminder(habit_id):
    """Отправка напоминания в Telegram"""
    try:
        habit = Habit.objects.get(id=habit_id)
    except Habit.DoesNotExist:
        return 'Привычка не найдена'

    # Получаем chat_id из профиля
    try:
        profile = habit.user.profile
        chat_id = profile.telegram_chat_id
    except UserProfile.DoesNotExist:
        return 'Профиль не найден'

    if not chat_id:
        return 'Telegram chat_id не указан'

    message = f'Напоминание: {habit.action} в {habit.time} в {habit.place}'
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'
    requests.post(url, data={'chat_id': chat_id, 'text': message})

    return f'Отправлено: {message}'


@shared_task
def check_habits():
    """Проверка привычек и отправка напоминаний"""
    habits = Habit.objects.filter(is_pleasant=False)

    count = 0
    for habit in habits:
        send_habit_reminder.delay(habit.id)
        count += 1

    return f'Обработано {count} привычек'