from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.pincode})"


class Tracking(models.Model):
    STATUS_CHOICES = (
        ('CREATED', 'Created'),
        ('PICKED', 'Picked Up'),
        ('TRANSIT', 'In Transit'),
        ('ARRIVED', 'Arrived at Hub'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
    )

    parcel = models.ForeignKey(
        'parcel.Parcel',
        on_delete=models.CASCADE,
        related_name='tracking_history'
    )

    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']