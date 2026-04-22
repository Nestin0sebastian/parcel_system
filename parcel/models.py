from django.db import models
import uuid
from django.contrib.auth.models import User


class Parcel(models.Model):
    STATUS_CHOICES = [
        ("CREATED", "Created"),
        ("CONFIRMED", "Confirmed"),
        ("IN_TRANSIT", "In Transit"),
        ("DELIVERED", "Delivered"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    tracking_id = models.CharField(max_length=100, unique=True, editable=False)

    sender_name = models.CharField(max_length=100)
    receiver_name = models.CharField(max_length=100)

    source_pincode = models.CharField(max_length=10)
    destination_pincode = models.CharField(max_length=10)

    weight = models.DecimalField(max_digits=5, decimal_places=2)
    dimensions = models.CharField(max_length=100, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="CREATED")

    is_confirmed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_id
    


