from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Parcel
from .serializers import ParcelSerializer
from tracking.models import Tracking, Location


class CreateParcelView(APIView):
    def post(self, request):
        serializer = ParcelSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            weight = float(data.get("weight"))
            source = data.get("source_pincode")
            dest = data.get("destination_pincode")
            dimensions = data.get("dimensions", "")

            base_price = 50
            per_kg = 20
            distance_factor = 1.5 if source != dest else 1

            volumetric_weight = 0
            if dimensions:
                try:
                    l, w, h = map(float, dimensions.split("x"))
                    volumetric_weight = (l * w * h) / 5000
                except:
                    volumetric_weight = 0

            chargeable_weight = max(weight, volumetric_weight)
            calculated_price = base_price + (chargeable_weight * per_kg * distance_factor)

           
            parcel = serializer.save(
                price=round(calculated_price, 2),
                status="CREATED"
            )

            
            location_obj, _ = Location.objects.get_or_create(name="Origin")

            Tracking.objects.create(
                parcel=parcel,
                location=location_obj,
                status="CREATED"
            )

            return Response({
                "message": "Parcel created successfully",
                "tracking_id": parcel.tracking_id,
                "price": parcel.price
            }, status=status.HTTP_201_CREATED)      

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class CalculatePriceView(APIView):
    def post(self, request):
        try:
            source_pincode = request.data.get("source_pincode")
            destination_pincode = request.data.get("destination_pincode")
            weight = float(request.data.get("weight", 0))
            dimensions = request.data.get("dimensions", "")

            base_price = 50
            per_kg = 20
            distance_factor = 1.5 if source_pincode != destination_pincode else 1

            volumetric_weight = 0
            if dimensions:
                try:
                    l, w, h = map(float, dimensions.split("x"))
                    volumetric_weight = (l * w * h) / 5000
                except:
                    volumetric_weight = 0

            chargeable_weight = max(weight, volumetric_weight)
            price = base_price + (chargeable_weight * per_kg * distance_factor)

            return Response({
                "price": round(price, 2),
                "chargeable_weight": round(chargeable_weight, 2)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)