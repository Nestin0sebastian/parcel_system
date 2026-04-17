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
            parcel = serializer.save()

            # ✅ create default location (Origin)
            location_obj, _ = Location.objects.get_or_create(name="Origin")

            # ✅ create tracking entry
            Tracking.objects.create(
                parcel=parcel,
                location=location_obj,
                status="CREATED"
            )

            return Response({
                "message": "Parcel created successfully",
                "tracking_id": parcel.tracking_id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)