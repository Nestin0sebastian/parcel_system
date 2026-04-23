from django.db import models
from django.contrib.auth.models import User


class Staff(models.Model):
    ROLE_CHOICES = [
        ("PICKUP", "Pickup"),
        ("HUB", "Hub"),
        ("DELIVERY", "Delivery"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    pincode = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"    

        