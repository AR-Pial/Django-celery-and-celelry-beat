from celery import shared_task


@shared_task
def say_hello():
    print("Hello! My first Celery task is running.")
    return "Success"