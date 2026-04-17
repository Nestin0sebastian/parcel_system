from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Parcel
from .serializers import ParcelSerializer
from tracking.models import Tracking


# 🔹 CREATE PARCEL API
class CreateParcelView(APIView):
    def post(self, request):
        serializer = ParcelSerializer(data=request.data)

        if serializer.is_valid():
            parcel = serializer.save()

            # create initial tracking
            Tracking.objects.create(
                parcel=parcel,
                location="Origin",
                status="CREATED"
            )

            return Response({
                "message": "Parcel created",
                "tracking_id": parcel.tracking_id
            })

        return Response(serializer.errors)