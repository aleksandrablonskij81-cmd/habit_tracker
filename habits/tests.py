from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from .models import Habit


class HabitAPITest(TestCase):
    """Тесты для API привычек"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test12345'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_habit(self):
        """Создание привычки"""
        response = self.client.post('/api/habits/', {
            'place': 'Парк',
            'time': '07:00',
            'action': 'Бег',
            'periodicity': 1,
            'duration': 60,
            'is_public': True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.user.id)

    def test_list_habits(self):
        """Список своих привычек"""
        Habit.objects.create(
            user=self.user,
            place='Парк',
            time='07:00',
            action='Бег',
            periodicity=1,
            duration=60,
            is_public=True
        )
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_update_habit(self):
        """Обновление привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='07:00',
            action='Бег',
            periodicity=1,
            duration=60,
            is_public=True
        )
        response = self.client.patch(f'/api/habits/{habit.id}/', {'action': 'Чтение'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'Чтение')

    def test_delete_habit(self):
        """Удаление привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='07:00',
            action='Бег',
            periodicity=1,
            duration=60,
            is_public=True
        )
        response = self.client.delete(f'/api/habits/{habit.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_anonymous_401(self):
        """Аноним получает 401"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_user_cannot_update(self):
        """Другой пользователь не может редактировать"""
        other = User.objects.create_user(username='other', password='test12345')
        habit = Habit.objects.create(
            user=other,
            place='Парк',
            time='07:00',
            action='Бег',
            periodicity=1,
            duration=60,
            is_public=False
        )
        response = self.client.patch(f'/api/habits/{habit.id}/', {'action': 'Взлом'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PublicHabitAPITest(TestCase):
    """Тесты для публичных привычек"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test12345'
        )
        self.client.force_authenticate(user=self.user)

    def test_public_habits_list(self):
        """Список публичных привычек"""
        Habit.objects.create(
            user=self.user,
            place='Парк',
            time='07:00',
            action='Бег',
            periodicity=1,
            duration=60,
            is_public=True
        )
        response = self.client.get('/api/public-habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_private_habits_not_in_public(self):
        """Приватные привычки не попадают в публичные"""
        Habit.objects.create(
            user=self.user,
            place='Дом',
            time='21:00',
            action='Чтение',
            periodicity=1,
            duration=60,
            is_public=False
        )
        response = self.client.get('/api/public-habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class HabitValidatorTest(TestCase):
    """Тесты валидаторов"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test12345')

    def test_duration_more_than_120(self):
        """Время выполнения > 120 секунд — ошибка"""
        from django.core.exceptions import ValidationError
        habit = Habit(
            user=self.user,
            place='Парк',
            time='07:00',
            action='Бег',
            duration=150
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_periodicity_more_than_7(self):
        """Периодичность > 7 дней — ошибка"""
        from django.core.exceptions import ValidationError
        habit = Habit(
            user=self.user,
            place='Парк',
            time='07:00',
            action='Бег',
            periodicity=10,
            duration=60
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_reward_and_related_habit(self):
        """Нельзя одновременно reward и related_habit"""
        from django.core.exceptions import ValidationError
        pleasant = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='21:00',
            action='Ванна',
            is_pleasant=True,
            duration=60
        )
        habit = Habit(
            user=self.user,
            place='Парк',
            time='07:00',
            action='Бег',
            reward='Десерт',
            related_habit=pleasant,
            duration=60
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()


class CeleryTasksTest(TestCase):
    """Тесты для Celery-задач"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test12345'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place='Парк',
            time='07:00',
            action='Бег',
            periodicity=1,
            duration=60,
            is_public=True
        )

    def test_check_habits(self):
        """Проверка задачи check_habits"""
        from habits.tasks import check_habits
        with patch('habits.tasks.send_habit_reminder.delay') as mock_delay:
            result = check_habits()
            self.assertIn('Обработано', result)
            mock_delay.assert_called()

    def test_send_habit_reminder_no_profile(self):
        """Отправка напоминания без профиля"""
        from habits.tasks import send_habit_reminder
        result = send_habit_reminder(self.habit.id)
        self.assertEqual(result, 'Профиль не найден')

    def test_send_habit_reminder_with_profile(self):
        """Отправка напоминания с профилем (без реальной отправки)"""
        from habits.tasks import send_habit_reminder
        from users.models import UserProfile

        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        profile.telegram_chat_id = '123456789'
        profile.save()

        with patch('habits.tasks.requests.post') as mock_post:
            result = send_habit_reminder(self.habit.id)
            self.assertIn('Отправлено', result)
            mock_post.assert_called_once()