from django.db import models
from django.contrib.auth.models import User
from . import utils
from django.utils import timezone
from django.core.exceptions import ValidationError



class MyLink(models.Model):
    source_link = models.CharField(max_length=300)
    hash = models.CharField(max_length=50, default=utils.generate_unique_hash, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)  # Add this field

    def is_expired(self):
        return self.expiration_date and self.expiration_date < timezone.now()

    def __str__(self):
        return self.hash
    
    def clean(self):
        if self.expiration_date and self.expiration_date < timezone.now():
            raise ValidationError("Expiration date cannot be in the past")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class ClickAnalytics(models.Model):
    link = models.ForeignKey(MyLink, on_delete=models.CASCADE, related_name="clicks")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Click on {self.link.hash} from {self.ip_address} at {self.timestamp}"
