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

            location_obj, _ = Location.objects.get_or_create(name="Origin")

            Tracking.objects.create(
                parcel=parcel,
                location=location_obj,
                status="CREATED"
            )

            return Response({
                "message": "Parcel created successfully",
                "parcel_id": parcel.id,
                "tracking_id": parcel.tracking_id,
                "price": parcel.price
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckoutView(APIView):
    def get(self, request, tracking_id):
        try:
            parcel = Parcel.objects.get(tracking_id=tracking_id)
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


class ConfirmParcelView(APIView):
    def post(self, request, tracking_id):
        try:
            parcel = Parcel.objects.get(tracking_id=tracking_id)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        if parcel.is_confirmed:
            return Response({
                "message": "Already confirmed",
                "parcel_id": parcel.id,
                "tracking_id": parcel.tracking_id
            }, status=400)

        parcel.is_confirmed = True
        parcel.status = "CONFIRMED"
        parcel.save()

        location_obj, _ = Location.objects.get_or_create(name="Confirmed")

        Tracking.objects.create(
            parcel=parcel,
            location=location_obj,
            status="PICKED"
        )

        return Response({
            "message": "Parcel confirmed successfully",
            "parcel_id": parcel.id,
            "tracking_id": parcel.tracking_id
        }, status=status.HTTP_200_OK)


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