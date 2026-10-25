from celery import shared_task
from django.conf import settings
import requests
from .models import Habit
from users.models import UserProfile

# ===== BOTGATE =====
BOTGATE_API_KEY = 'bg_live_a5e2103e73bdfe4e199f7da280d9a692'
BOTGATE_BOT_ID = 'bot_bftfrNDogdzz'
BOTGATE_BASE_URL = 'https://bot-gate.ru/api/v1'


@shared_task
def send_habit_reminder(habit_id):
    """Отправка напоминания в Telegram через BotGate"""
    try:
        habit = Habit.objects.get(id=habit_id)
    except Habit.DoesNotExist:
        return 'Привычка не найдена'

    try:
        profile = habit.user.profile
        chat_id = profile.telegram_chat_id
    except UserProfile.DoesNotExist:
        return 'Профиль не найден'

    if not chat_id:
        return 'Telegram chat_id не указан'

    message = f'Напоминание: {habit.action} в {habit.time} в {habit.place}'

    # 👇 ПРАВИЛЬНЫЙ URL: /api/v1/bots/{botPublicId}/{method}
    url = f'{BOTGATE_BASE_URL}/bots/{BOTGATE_BOT_ID}/sendMessage'

    headers = {
        'Authorization': f'Bearer {BOTGATE_API_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(
            url,
            json={'chat_id': chat_id, 'text': message},
            headers=headers,
            timeout=10
        )
        if response.status_code != 200:
            return f'Ошибка BotGate: {response.status_code} {response.text}'
    except requests.RequestException as e:
        return f'Ошибка запроса: {str(e)}'

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