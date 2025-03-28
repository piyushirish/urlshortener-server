from celery import shared_task
from django.utils import timezone
from .models import MyLink

@shared_task
def delete_expired_links():
    expired_links = MyLink.objects.filter(
        expiration_date__lte=timezone.now()
    )
    count = expired_links.count()
    expired_links.delete()
    return f"Deleted {count} expired links"