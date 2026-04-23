from rest_framework import serializers
from .models import Tracking, Location

class TrackingSerializer(serializers.ModelSerializer):
    parcel_tracking_id = serializers.CharField(source='parcel.tracking_id', read_only=True)

    location_name = serializers.CharField(source='location.name', read_only=True)
    pincode = serializers.CharField(source='location.pincode', read_only=True)
    city = serializers.CharField(source='location.city', read_only=True)
    state = serializers.CharField(source='location.state', read_only=True)

    time = serializers.DateTimeField(source='timestamp', format="%Y-%m-%d %H:%M", read_only=True)

    # 🔥 NEW FIELDS
    note = serializers.CharField(read_only=True)
    eta = serializers.SerializerMethodField()

    class Meta:
        model = Tracking
        fields = [
            "parcel_tracking_id",
            "status",
            "location_name",
            "pincode",
            "city",
            "state",
            "time",
            "note",   # 🔥 added
            "eta"     # 🔥 added
        ]

    # 🔥 ETA DISPLAY LOGIC
    def get_eta(self, obj):
        if obj.eta_days:
            return f"{obj.eta_days} day(s) remaining"
        return None