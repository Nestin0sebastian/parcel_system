from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone


class Parcel(models.Model):
    STATUS_CHOICES = [
        ("CREATED", "Created"),
        ("CONFIRMED", "Confirmed"),
        ("ASSIGNED", "Assigned"),
        ("PICKED", "Picked"),
        ("ARRIVED", "Arrived at Hub"),
        ("IN_TRANSIT", "In Transit"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
    ]

    # 👤 USER
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # 🔑 TRACKING
    tracking_id = models.CharField(max_length=100, unique=True, editable=False)

    # 👥 SENDER & RECEIVER
    sender_name = models.CharField(max_length=100)
    sender_phone = models.CharField(max_length=15)

    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=15)
    receiver_email = models.EmailField(max_length=255, null=True, blank=True)
    # 📍 LOCATION
    source_pincode = models.CharField(max_length=10)
    destination_pincode = models.CharField(max_length=10)

    # 📦 DETAILS
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    dimensions = models.CharField(max_length=100, blank=True)

    # 💰 PRICE
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # 📊 STATUS
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="CREATED"
    )
    is_confirmed = models.BooleanField(default=False)

    # 🚚 DELIVERY SYSTEM
    assigned_delivery_staff = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )

    # 🔐 OTP SYSTEM
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_verified = models.BooleanField(default=False)
    otp_created_at = models.DateTimeField(null=True, blank=True)  # 🔥 for expiry

    # ⏱️ TIME
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔄 AUTO TRACKING ID
    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_id