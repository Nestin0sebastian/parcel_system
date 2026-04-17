from django.db import models
import uuid


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