from rest_framework import serializers
from .models import Tracking


class TrackingSerializer(serializers.ModelSerializer):
    parcel_tracking_id = serializers.CharField(source='parcel.tracking_id', read_only=True)

    class Meta:
        model = Tracking
        fields = '__all__'