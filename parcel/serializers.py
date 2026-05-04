from rest_framework import serializers
from .models import Parcel
from core.utils import (
    get_location_from_pincode,
    calculate_price_from_data,
)


class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = '__all__'
        read_only_fields = [
            'tracking_id',
            'created_at',
            'price',
            'status',
            'is_confirmed'
        ]

    def validate(self, data):
        source = data.get("source_pincode")
        destination = data.get("destination_pincode")

        if not get_location_from_pincode(source):
            raise serializers.ValidationError({
                "source_pincode": "Invalid source pincode"
            })

        if not get_location_from_pincode(destination):
            raise serializers.ValidationError({
                "destination_pincode": "Invalid destination pincode"
            })

        return data

    def create(self, validated_data):
        weight = float(validated_data.get("weight"))
        source = validated_data.get("source_pincode")
        dest = validated_data.get("destination_pincode")
        dimensions = validated_data.get("dimensions", "")

        pricing = calculate_price_from_data(weight, source, dest, dimensions)

        # 🔥 STORE ONLY TOTAL IN DB
        validated_data['price'] = pricing["total"]

        validated_data['status'] = "PENDING"  
        validated_data['is_confirmed'] = False

        return super().create(validated_data)