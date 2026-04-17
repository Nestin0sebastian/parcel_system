from rest_framework.views import APIView
from rest_framework.response import Response

from parcel.models import Parcel
from .models import Tracking
from .serializers import TrackingSerializer


# 🔹 TRACK PARCEL API
class TrackParcelView(APIView):
    def get(self, request, tracking_id):
        try:
            parcel = Parcel.objects.get(tracking_id=tracking_id)
            tracking = parcel.tracking_history.all()

            data = TrackingSerializer(tracking, many=True).data

            return Response({
                "tracking_id": tracking_id,
                "history": data
            })

        except Parcel.DoesNotExist:
            return Response({
                "error": "Parcel not found"
            })


# 🔹 UPDATE TRACKING (STAFF)
class UpdateTrackingView(APIView):
    def post(self, request):
        tracking_id = request.data.get('tracking_id')

        try:
            parcel = Parcel.objects.get(tracking_id=tracking_id)

            Tracking.objects.create(
                parcel=parcel,
                location=request.data.get('location'),
                status=request.data.get('status')
            )

            return Response({
                "message": "Tracking updated"
            })

        except Parcel.DoesNotExist:
            return Response({
                "error": "Parcel not found"
            })