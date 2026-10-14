# Django Celery Beat Demo

A simple Django project demonstrating asynchronous background tasks and periodic task scheduling using **Django, Celery, Redis, and django-celery-beat**.

This project demonstrates two ways to schedule recurring tasks:

1. **Settings-based scheduler:** Define schedules in `config/settings.py`.
2. **Database-based scheduler:** Create and manage schedules through Django Admin.

## Technologies Used

- Python
- Django
- Celery
- Redis
- django-celery-beat
- SQLite (default Django database)

## Project Features

- Configured Celery with Django.
- Created background tasks using `shared_task`.
- Used Redis as the Celery message broker.
- Executed tasks asynchronously using a Celery Worker.
- Scheduled recurring tasks using Celery Beat.
- Configured schedules using `CELERY_BEAT_SCHEDULE`.
- Managed periodic tasks through Django Admin using `django-celery-beat`.
- Configured the timezone to `Asia/Dhaka`.

## Project Structure

```text
django-beat-demo/
├── config/
│   ├── __init__.py
│   ├── celery.py
│   ├── settings.py
│   └── urls.py
├── core/
│   ├── __init__.py
│   ├── apps.py
│   └── tasks.py
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

Replace `<repository-url>` with your Git repository URL.

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you do not have a `requirements.txt` file yet, install the dependencies:

```bash
pip install django celery redis django-celery-beat
pip freeze > requirements.txt
```

### 4. Start Redis

Make sure Redis Server is installed.

On Ubuntu or Debian:

```bash
sudo service redis-server start
```

Check whether Redis is running:

```bash
redis-cli ping
```

Expected output:

```text
PONG
```

### 5. Configure Django Settings

In `config/settings.py`, add the following configuration:

```python
INSTALLED_APPS = [
    # Default Django apps...
    "django_celery_beat",
    "core",
]

CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"

CELERY_TIMEZONE = "Asia/Dhaka"
CELERY_ENABLE_UTC = True
```

Keep your existing Django applications in `INSTALLED_APPS`.

### 6. Apply Database Migrations

```bash
python manage.py migrate
```

This creates the database tables required by Django and `django-celery-beat`.

### 7. Create a Superuser (Optional)

To manage schedules through Django Admin:

```bash
python manage.py createsuperuser
```

## Celery Configuration

Configure Celery in `config/celery.py`:

```python
import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

app = Celery("config")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)

app.autodiscover_tasks()
```

In `config/__init__.py`:

```python
from .celery import app as celery_app

__all__ = ("celery_app",)
```

This configuration allows Celery to load Django settings and automatically discover tasks in installed Django applications.

## Example Background Task

Create a task in `core/tasks.py`:

```python
from celery import shared_task


@shared_task
def say_hello():
    print("Hello! My first Celery task is running.")
    return "Success"
```

## Running the Project

Open separate terminals from the project directory and activate the virtual environment in each terminal.

### Terminal 1: Redis

Redis should be running before the Worker and Beat start.

```bash
sudo service redis-server start
```

### Terminal 2: Celery Worker

```bash
celery -A config worker --loglevel=info
```

The Worker receives and executes tasks.

### Terminal 3: Celery Beat

Choose **one** of the scheduler commands below, depending on which scheduling method you want to use.

For the settings-based scheduler:

```bash
celery -A config beat --loglevel=info
```

For the database-based scheduler:

```bash
celery -A config beat \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler \
    --loglevel=info
```

Do not run multiple Beat processes for the same schedule. That can cause duplicate task execution.

### Terminal 4: Django Development Server (Optional)

```bash
python manage.py runserver
```

The development server is needed for Django Admin and HTTP endpoints, but not for standalone scheduled tasks.

## Executing a Task Manually

You can execute a task immediately without using Celery Beat.

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

The Worker executes the task asynchronously.

**Note:** Redis and the Celery Worker must be running. Celery Beat is not required for manual task execution.

## Scheduling Method 1: Settings-Based Scheduler

In this method, schedules are defined in `config/settings.py` using `CELERY_BEAT_SCHEDULE`.

### Example 1: Run Every 10 Seconds

Add this to `config/settings.py`:

```python
CELERY_BEAT_SCHEDULE = {
    "say-hello-every-10-seconds": {
        "task": "core.tasks.say_hello",
        "schedule": 10.0,
    },
}
```

The task will be scheduled every 10 seconds while Beat is running.

### Example 2: Run Daily at 9:00 AM

Import `crontab` and configure the schedule:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "say-hello-every-day-at-9am": {
        "task": "core.tasks.say_hello",
        "schedule": crontab(
            hour=9,
            minute=0,
        ),
    },
}
```

The schedule uses the configured Celery timezone.

### Timezone Configuration

In `config/settings.py`:

```python
CELERY_TIMEZONE = "Asia/Dhaka"
CELERY_ENABLE_UTC = True
```

This configures Celery's schedule interpretation for Bangladesh time.

### How to Run

Start the Worker:

```bash
celery -A config worker --loglevel=info
```

Start Beat using the default scheduler:

```bash
celery -A config beat --loglevel=info
```

Restart Beat after modifying a settings-based schedule so the changes are loaded.

### When to Use This Method

- Schedules are part of the application code.
- You want schedules tracked in Git.
- The schedule is relatively static.
- You prefer configuration managed by developers.

## Scheduling Method 2: Database-Based Scheduler

The database-based scheduler uses `django-celery-beat` to store schedules in the Django database.

You can create, edit, enable, or disable periodic tasks through Django Admin without changing `CELERY_BEAT_SCHEDULE` in your code.

### Step 1: Enable django-celery-beat

Make sure `config/settings.py` contains:

```python
INSTALLED_APPS = [
    # Default Django apps...
    "django_celery_beat",
    "core",
]
```

Run migrations:

```bash
python manage.py migrate
```

### Step 2: Open Django Admin

Start the development server:

```bash
python manage.py runserver
```

Visit:

```text
http://127.0.0.1:8000/admin/
```

Log in using your superuser account.

### Step 3: Create an Interval Schedule

Navigate to:

**Periodic Tasks → Intervals → Add**

Configure:

| Field | Value |
|---|---|
| Every | `10` |
| Period | `seconds` |

Save the schedule.

### Step 4: Create a Periodic Task

Navigate to:

**Periodic Tasks → Periodic tasks → Add**

Configure:

| Field | Value |
|---|---|
| Name | `say-hello-every-10-seconds` |
| Task (registered) | `core.tasks.say_hello` |
| Interval Schedule | `Every 10 seconds` |
| Enabled | Checked |
| Description | Optional |

Leave `Task (custom)` empty because `core.tasks.say_hello` is already registered.

Save the task.

### Step 5: Start the Worker

```bash
celery -A config worker --loglevel=info
```

### Step 6: Start Beat with the Database Scheduler

```bash
celery -A config beat \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler \
    --loglevel=info
```

The database scheduler reads the enabled periodic task from the database and sends it to the Worker according to its schedule.

### Other Schedule Types

`django-celery-beat` supports several schedule types:

- **Intervals:** Run every 10 seconds, 5 minutes, or another fixed interval.
- **Crontabs:** Run at a specific time, day, or date, such as every day at 9:00 AM.
- **Clocked:** Schedule a task for a specific date and time, typically for one-time execution.
- **Solar events:** Schedule tasks based on events such as sunrise or sunset.

### When to Use This Method

- Schedules need to be managed through Django Admin.
- Non-developers need to change task schedules.
- Tasks need to be enabled or disabled without changing application code.
- Schedules are stored and managed in the database.

## Settings-Based vs. Database-Based Scheduling

| Feature | Settings-Based | Database-Based |
|---|---|---|
| Schedule storage | `settings.py` | Django database |
| Manage through Admin | No, not by default | Yes |
| Change schedule | Edit code and restart Beat | Update database schedule |
| Git version control | Straightforward | Requires separate handling for schedule data |
| Best for | Static schedules | Dynamic schedules |
| Beat command | Default scheduler | `DatabaseScheduler` |

**Important:** Choose the appropriate scheduler command for the schedules you want to run. If the same task is configured in both systems, it may be triggered more than once.

The database scheduler can also have its own `celery.backend_cleanup` periodic task. This is a Celery maintenance task for cleaning up expired task results when the configured result backend supports that operation. It is separate from your `core.tasks.say_hello` example.

## How It Works

The main components work together as follows:

1. **Django:** Defines the application and its tasks.
2. **Celery Beat:** Determines when periodic tasks should be sent.
3. **Redis:** Acts as the message broker, carrying task messages.
4. **Celery Worker:** Receives and executes task messages.
5. **django-celery-beat:** Stores database-backed schedules and makes them manageable through Django Admin.

### Task Execution Flow

```text
Settings Scheduler or Database Scheduler
                  |
                  v
             Celery Beat
                  |
                  v
                Redis
                  |
                  v
            Celery Worker
                  |
                  v
          Execute Django Task
```

## Troubleshooting

### Task Is Not Executing

Check the following:

- Redis is running.
- The Celery Worker is running.
- Celery Beat is running with the intended scheduler.
- The task name is correct: `core.tasks.say_hello`.
- The periodic task is enabled.
- The correct schedule is configured.

### Task Is Not Appearing in the Admin Dropdown

Make sure the task is registered, the Django app is installed, and the Worker/Beat processes are using the correct project configuration. Restart processes after changing task code.

### Duplicate Task Execution

Check whether:

- More than one Beat process is running.
- The same task is scheduled in both `CELERY_BEAT_SCHEDULE` and the database.
- Duplicate periodic task entries exist in Django Admin.

### Task Results and Backend Cleanup

The message broker and the result backend serve different purposes. Redis is configured here as the broker; a result backend must also be configured if you want to store task results. Celery's backend cleanup task is relevant when result storage is enabled and supports expiration and cleanup.

## Important Notes

- Keep Redis, the Worker, and Beat running while scheduled tasks are expected to execute.
- Django's development server is optional for background task execution.
- Use one active Beat scheduler process for a given schedule.
- Restart Beat after modifying settings-based schedules.
- Database schedules can be managed in Django Admin.
- Keep secrets and production credentials out of version control.

## License

For learning and educational purposes.
