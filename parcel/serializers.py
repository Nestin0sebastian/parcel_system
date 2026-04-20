from rest_framework import serializers
from .models import Parcel
from core.utils import get_location_from_pincode


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

    # 🔥 PINCODE VALIDATION
    def validate(self, data):
        source = data.get("source_pincode")
        destination = data.get("destination_pincode")

        source_data = get_location_from_pincode(source)
        dest_data = get_location_from_pincode(destination)

        if not source_data:
            raise serializers.ValidationError({
                "source_pincode": "Invalid source pincode"
            })

        if not dest_data:
            raise serializers.ValidationError({
                "destination_pincode": "Invalid destination pincode"
            })

        return data

    # 🔥 PRICE CALCULATION
    def create(self, validated_data):
        weight = float(validated_data.get("weight"))
        source = validated_data.get("source_pincode")
        dest = validated_data.get("destination_pincode")
        dimensions = validated_data.get("dimensions", "")

        base_price = 50
        per_kg = 20
        distance_factor = 1.5 if source != dest else 1

        volumetric_weight = 0
        if dimensions:
            try:
                l, w, h = map(float, dimensions.split("x"))
                volumetric_weight = (l * w * h) / 5000
            except Exception:
                raise serializers.ValidationError(
                    "Invalid dimensions format. Use LxWxH"
                )

        chargeable_weight = max(weight, volumetric_weight)
        calculated_price = base_price + (chargeable_weight * per_kg * distance_factor)

        validated_data['price'] = round(calculated_price, 2)
        validated_data['status'] = "PENDING"
        validated_data['is_confirmed'] = False

        return super().create(validated_data)