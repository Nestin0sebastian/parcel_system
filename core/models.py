from django.db import models
import uuid


class User(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('STAFF', 'Staff'),
        ('USER', 'User'),
    )

    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')

    def __str__(self):
        return self.username






class Parcel(models.Model):
    tracking_id = models.CharField(max_length=100, unique=True, editable=False)

    sender_name = models.CharField(max_length=100)
    receiver_name = models.CharField(max_length=100)

    source_pincode = models.CharField(max_length=10)
    destination_pincode = models.CharField(max_length=10)

    weight = models.FloatField()
    dimensions = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_id







class Tracking(models.Model):
    STATUS_CHOICES = (
        ('CREATED', 'Created'),
        ('PICKED', 'Picked Up'),
        ('TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
    )

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name='tracking_history')

    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parcel.tracking_id} - {self.status}"