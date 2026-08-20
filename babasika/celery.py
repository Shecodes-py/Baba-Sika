import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "babasika.settings")

app = Celery("babasika")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "expire-pending-actions": {
        "task": "pensions.tasks.expire_pending_actions_task",
        "schedule": 60.0,  # every minute - PendingAction TTLs are short (default 15 min)
    },
    "expire-magic-links": {
        "task": "dashboard_bridge.tasks.expire_magic_links_task",
        "schedule": crontab(minute="*/5"),
    },
    "retry-pfa-registrations": {
        "task": "pensions.tasks.retry_pfa_registrations_task",
        "schedule": crontab(minute="*/10"),
    },
    "send-savings-nudges": {
        "task": "conversations.tasks.send_savings_nudges_task",
        "schedule": crontab(hour=9, minute=0),  # daily 09:00 server time - revisit once timezone/cadence is confirmed
    },
}
