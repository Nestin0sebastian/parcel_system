from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Parcel
from .serializers import ParcelSerializer
from tracking.models import Tracking, Location
from core.utils import get_location_from_pincode


# ✅ CREATE PARCEL
class CreateParcelView(APIView):
    def post(self, request):
        serializer = ParcelSerializer(data=request.data)

        if serializer.is_valid():
            parcel = serializer.save()

            return Response({
                "message": "Parcel created successfully",
                "parcel_id": parcel.id,
                "price": parcel.price
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ CHECKOUT (USING PARCEL ID)
class CheckoutView(APIView):
    def get(self, request, parcel_id):
        try:
            parcel = Parcel.objects.get(id=parcel_id)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        return Response({
            "parcel_id": parcel.id,
            "tracking_id": parcel.tracking_id,
            "sender": parcel.sender_name,
            "receiver": parcel.receiver_name,
            "source": parcel.source_pincode,
            "destination": parcel.destination_pincode,
            "weight": parcel.weight,
            "dimensions": parcel.dimensions,
            "price": parcel.price,
            "status": parcel.status,
            "is_confirmed": parcel.is_confirmed
        })


# ✅ CONFIRM PARCEL (STARTS TRACKING)
class ConfirmParcelView(APIView):
    def post(self, request, parcel_id):
        try:
            parcel = Parcel.objects.get(id=parcel_id)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        if parcel.is_confirmed:
            return Response({
                "message": "Already confirmed",
                "parcel_id": parcel.id,
                "tracking_id": parcel.tracking_id
            }, status=400)

        # 🔥 Confirm parcel
        parcel.is_confirmed = True
        parcel.status = "CONFIRMED"
        parcel.save()

        # 🔥 Get location from pincode
        location_data = get_location_from_pincode(parcel.source_pincode)

        if location_data:
            location_obj = Location.objects.create(
                name=location_data["name"],
                pincode=parcel.source_pincode,
                city=location_data["city"],
                state=location_data.get("state")
            )
        else:
            location_obj = Location.objects.create(
                name="Unknown",
                pincode=parcel.source_pincode,
                city="Unknown"
            )

        # 🔥 Create first tracking entry
        Tracking.objects.create(
            parcel=parcel,
            location=location_obj,
            status="CREATED"
        )

        return Response({
            "message": "Parcel confirmed successfully",
            "parcel_id": parcel.id,
            "tracking_id": parcel.tracking_id
        }, status=status.HTTP_200_OK)


# ✅ INVOICE (USES TRACKING ID)
class InvoiceView(APIView):
    def get(self, request, tracking_id):
        try:
            parcel = Parcel.objects.get(tracking_id=tracking_id)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        if not parcel.is_confirmed:
            return Response({"error": "Parcel not confirmed yet"}, status=400)

        return Response({
            "invoice_id": f"INV-{parcel.id}",
            "parcel_id": parcel.id,
            "tracking_id": parcel.tracking_id,
            "sender": parcel.sender_name,
            "receiver": parcel.receiver_name,
            "source": parcel.source_pincode,
            "destination": parcel.destination_pincode,
            "weight": parcel.weight,
            "dimensions": parcel.dimensions,
            "price": parcel.price,
            "status": parcel.status,
            "created_at": parcel.created_at
        })