# Habit Tracker

Курсовая работа: трекер полезных привычек с Telegram-ботом.

## Технологии

- Python 3.14
- Django 6.1
- DRF
- Celery
- Redis
- PostgreSQL
- Telegram Bot API

## Установка

1. Клонировать репозиторий
2. Создать виртуальное окружение: `python -m venv .venv`
3. Активировать: `source .venv/bin/activate`
4. Установить зависимости: `pip install -r requirements.txt`
5. Создать `.env` по примеру `.env.template`
6. Применить миграции: `python manage.py migrate`
7. Запустить сервер: `python manage.py runserver`

## Запуск Celery

```bash
celery -A config worker -l info --pool=solo
celery -A config beat -l info