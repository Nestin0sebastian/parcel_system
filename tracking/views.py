from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from parcel.models import Parcel
from .models import Tracking, Location
from .serializers import TrackingSerializer
from core.utils import get_location_from_pincode
from core.utils import estimate_eta

ALLOWED_TRANSITIONS = {
    "CREATED": ["PICKED_UP"],
    "PICKED_UP": ["ARRIVED_AT_SENDER_HUB"],
    "ARRIVED_AT_SENDER_HUB": ["IN_TRANSIT"],
    "IN_TRANSIT": ["ARRIVED_AT_DESTINATION_HUB"],
    "ARRIVED_AT_DESTINATION_HUB": ["OUT_FOR_DELIVERY"],
    "OUT_FOR_DELIVERY": ["DELIVERED"],
}
# 🔹 TRACK PARCEL API
class TrackParcelView(APIView):
    def get(self, request, tracking_id):
        try:
            parcel = Parcel.objects.get(tracking_id=tracking_id)

            tracking_qs = parcel.tracking_history.all()

            if not tracking_qs.exists():
                return Response({
                    "error": "No tracking history found"
                }, status=404)

            serializer = TrackingSerializer(tracking_qs, many=True)

            return Response({
                "tracking_id": tracking_id,
                "total_updates": tracking_qs.count(),
                "history": serializer.data
            })

        except Parcel.DoesNotExist:
            return Response({
                "error": "Parcel not found"
            }, status=404)


class UpdateTrackingView(APIView):
    def post(self, request):
        print("🔥 FINAL VIEW RUNNING")

        tracking_id = request.data.get('tracking_id')
        new_status = request.data.get('status')

        # ✅ Validate input
        if not tracking_id or not new_status:
            return Response({
                "error": "tracking_id and status required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            parcel = Parcel.objects.get(tracking_id=tracking_id)
        except Parcel.DoesNotExist:
            return Response({
                "error": "Parcel not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # 🔥 STATUS CONTROL
        last_tracking = parcel.tracking_history.last()

        if last_tracking:
            current_status = last_tracking.status
            allowed = ALLOWED_TRANSITIONS.get(current_status, [])

            if new_status not in allowed:
                return Response({
                    "error": f"Invalid transition from {current_status} → {new_status}"
                }, status=status.HTTP_400_BAD_REQUEST)

        # 🔥 AUTO SELECT PINCODE
        if new_status in ["PICKED_UP", "ARRIVED_AT_SENDER_HUB"]:
            pincode = parcel.source_pincode

        elif new_status in ["ARRIVED_AT_DESTINATION_HUB", "OUT_FOR_DELIVERY", "DELIVERED"]:
            pincode = parcel.destination_pincode

        elif new_status == "IN_TRANSIT":
            pincode = parcel.destination_pincode

        else:
            pincode = parcel.source_pincode

        # 🔥 CREATE LOCATION
        location_data = get_location_from_pincode(pincode)

        if location_data:
            location_obj = Location.objects.create(
                name=location_data.get("name", "Unknown"),
                pincode=pincode,
                city=location_data.get("city", "Unknown"),
                state=location_data.get("state", "Unknown")
            )
            current_city = location_data.get("city", "Unknown")
        else:
            location_obj = Location.objects.create(
                name="Unknown",
                pincode=pincode,
                city="Unknown",
                state="Unknown"
            )
            current_city = "Unknown"

        print("LOCATION CREATED:", location_obj.id)

        # 🔥 DYNAMIC NOTE LOGIC
        note = ""

        if new_status == "PICKED_UP":
            note = "Parcel picked up"

        elif new_status == "ARRIVED_AT_SENDER_HUB":
            note = current_city

        elif new_status == "IN_TRANSIT":
            sender_loc = get_location_from_pincode(parcel.source_pincode)
            receiver_loc = get_location_from_pincode(parcel.destination_pincode)

            sender_city = sender_loc.get("city") if sender_loc else "Unknown"
            receiver_city = receiver_loc.get("city") if receiver_loc else "Unknown"

            note = f"{sender_city} → {receiver_city}"

        elif new_status == "ARRIVED_AT_DESTINATION_HUB":
            note = current_city

        elif new_status == "OUT_FOR_DELIVERY":
            note = "Out for delivery"

        elif new_status == "DELIVERED":
            note = "Delivered successfully"

        # 🔥 GET CITIES (FOR ETA)
        sender_loc = get_location_from_pincode(parcel.source_pincode)
        receiver_loc = get_location_from_pincode(parcel.destination_pincode)

        sender_city = sender_loc.get("city") if sender_loc else "Unknown"
        receiver_city = receiver_loc.get("city") if receiver_loc else "Unknown"

        # 🔥 ETA CALCULATION
        eta_days = None
        if new_status in ["PICKED_UP", "IN_TRANSIT"]:
            eta_days = estimate_eta(sender_city, receiver_city)

        # ✅ CREATE TRACKING
        Tracking.objects.create(
            parcel=parcel,
            location=location_obj,
            status=new_status,
            note=note,
            eta_days=eta_days
        )

        # 🔥 SYNC PARCEL STATUS
        parcel.status = new_status
        parcel.save()

        return Response({
            "message": "Tracking updated successfully",
            "new_status": new_status,
            "note": note,
            "eta_days": eta_days
        }, status=status.HTTP_200_OK)