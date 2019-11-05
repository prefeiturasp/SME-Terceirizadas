import time

from celery import shared_task


@shared_task
def task_lenta():
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXX TASK' * 100)
    time.sleep(20)
    return True
