# Django Celery Beat Demo

A simple Django project demonstrating background tasks using Celery, Redis, and Celery Beat.

## Technologies Used

- Python
- Django
- Celery
- Redis
- django-celery-beat

## Project Features

- Configured Celery with Django.
- Created a background task using `shared_task`.
- Used Redis as the Celery message broker.
- Executed tasks asynchronously using a Celery Worker.
- Learned periodic task scheduling with Celery Beat.
- Configured task schedules using `CELERY_BEAT_SCHEDULE`.

## Project Structure

```text
django-beat-demo/
├── config/
│   ├── __init__.py
│   ├── celery.py
│   ├── settings.py
│   └── urls.py
├── core/
│   ├── tasks.py
│   └── apps.py
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd django-beat-demo
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Redis

Make sure Redis is installed, then run:

```bash
sudo service redis-server start
```

Check Redis:

```bash
redis-cli ping
```

Expected output:

```text
PONG
```

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

## Running the Project

Open separate terminals for the following processes.

### Terminal 1: Celery Worker

```bash
celery -A config worker --loglevel=info
```

### Terminal 2: Celery Beat

```bash
celery -A config beat --loglevel=info
```

### Terminal 3: Django Development Server (Optional)

```bash
python manage.py runserver
```

The Django server is optional when running background tasks that do not require HTTP requests.

## Example Task

The task is defined in `core/tasks.py`:

```python
from celery import shared_task

@shared_task
def say_hello():
    print("Hello! My first Celery task is running.")
    return "Success"
```

### Execute the Task Manually

Open the Django shell:

```bash
python manage.py shell
```

Run:

```python
from core.tasks import say_hello

result = say_hello.delay()
print(result.id)
```

The Celery Worker will execute the task.

## Periodic Task Scheduling

Configure `CELERY_BEAT_SCHEDULE` in `config/settings.py`.

Example: Run the task every 10 seconds.

```python
CELERY_BEAT_SCHEDULE = {
    "say-hello-every-10-seconds": {
        "task": "core.tasks.say_hello",
        "schedule": 10.0,
    },
}
```

For a daily schedule, import `crontab`:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "say-hello-every-day-at-9am": {
        "task": "core.tasks.say_hello",
        "schedule": crontab(hour=9, minute=0),
    },
}
```

The timezone is configured as:

```python
CELERY_TIMEZONE = "Asia/Dhaka"
CELERY_ENABLE_UTC = True
```

Restart Celery Beat after changing a settings-based schedule.

## How It Works

- **Django:** Sends task requests.
- **Celery Beat:** Schedules periodic tasks.
- **Redis:** Acts as the message broker.
- **Celery Worker:** Executes tasks.

## Notes

- Redis, Celery Worker, and Celery Beat must be running for scheduled tasks to execute.
- Django's development server is not required for standalone background tasks.
- `django-celery-beat` is installed, but database-backed scheduling requires adding it to `INSTALLED_APPS`, running migrations, and starting Beat with the database scheduler.

## License

For learning and educational purposes.