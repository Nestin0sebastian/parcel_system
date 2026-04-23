from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import authenticate, login, logout

from .models import Parcel
from .serializers import ParcelSerializer
from tracking.models import Tracking, Location
from core.utils import get_location_from_pincode




class CreateParcelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ParcelSerializer(data=request.data)

        if serializer.is_valid():
            existing = Parcel.objects.filter(
                user=request.user,
                sender_name=request.data.get("sender_name"),
                receiver_name=request.data.get("receiver_name"),
                source_pincode=request.data.get("source_pincode"),
                destination_pincode=request.data.get("destination_pincode"),
                weight=request.data.get("weight"),
                dimensions=request.data.get("dimensions"),
                is_confirmed=False
            ).first()

            if existing:
                return Response({
                    "message": "Parcel already created",
                    "parcel_id": existing.id,
                    "price": existing.price
                }, status=200)

            parcel = serializer.save(user=request.user)

            return Response({
                "message": "Parcel created successfully",
                "parcel_id": parcel.id,
                "price": parcel.price
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcel_id):
        try:
            parcel = Parcel.objects.get(id=parcel_id, user=request.user)
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
    permission_classes = [IsAuthenticated]

    def post(self, request, parcel_id):
        try:
            parcel = Parcel.objects.get(id=parcel_id, user=request.user)
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

        location_data = get_location_from_pincode(parcel.source_pincode)

        if location_data:
            location_obj = Location.objects.create(
                name=location_data["name"],
                pincode=parcel.source_pincode,
                city=location_data["city"]
            )
        else:
            location_obj = Location.objects.create(
                name="Unknown",
                pincode=parcel.source_pincode,
                city="Unknown"
            )

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


class InvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tracking_id):
        try:
            parcel = Parcel.objects.get(tracking_id=tracking_id, user=request.user)
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
     
class UserParcelListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parcels = Parcel.objects.filter(user=request.user).order_by('-created_at')

        data = []

        for p in parcels:
            data.append({
                "parcel_id": p.id,
                "tracking_id": p.tracking_id,
                "sender": p.sender_name,
                "receiver": p.receiver_name,
                "source": p.source_pincode,
                "destination": p.destination_pincode,
                "status": p.status,
                "created_at": p.created_at
            })

        return Response(data)


class UserParcelDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcel_id):
        try:
            parcel = Parcel.objects.get(id=parcel_id, user=request.user)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        # Parcel info
        parcel_data = {
            "parcel_id": parcel.id,
            "tracking_id": parcel.tracking_id,
            "sender": parcel.sender_name,
            "receiver": parcel.receiver_name,
            "source": parcel.source_pincode,
            "destination": parcel.destination_pincode,
            "weight": parcel.weight,
            "price": parcel.price,
            "status": parcel.status,
            "created_at": parcel.created_at
        }

        # Tracking history
        history = parcel.tracking_history.all()

        tracking_data = [
            {
                "status": t.status,
                "location": t.location.city,
                "note": t.note,
                "time": t.timestamp
            }
            for t in history
        ]

        return Response({
            "parcel": parcel_data,
            "tracking_history": tracking_data
        })

                    
class StaffDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        staff = getattr(request.user, "staff", None)

        if not staff:
            return Response({"error": "Not staff"}, status=403)

        parcels = Parcel.objects.filter(assigned_staff=staff)

        total = parcels.count()

        response = {
            "staff": request.user.username,
            "role": staff.role,
            "total_assigned": total,
        }

        # 🔵 PICKUP STAFF DASHBOARD
        if staff.role == "PICKUP":
            pending = parcels.exclude(
                status__in=["PICKED_UP", "CANCELLED"]
            ).count()

            picked = parcels.filter(status="PICKED_UP").count()
            cancelled = parcels.filter(status="CANCELLED").count()

            response.update({
                "pending_pickups": pending,
                "picked": picked,
                "cancelled": cancelled
            })

        # 🟡 HUB STAFF DASHBOARD
        elif staff.role == "HUB":
            arrived = parcels.filter(status="ARRIVED_AT_SENDER_HUB").count()
            in_transit = parcels.filter(status="IN_TRANSIT").count()
            arrived_dest = parcels.filter(status="ARRIVED_AT_DESTINATION_HUB").count()

            response.update({
                "arrived_at_sender_hub": arrived,
                "in_transit": in_transit,
                "arrived_at_destination_hub": arrived_dest
            })

        # 🟢 DELIVERY STAFF DASHBOARD
        elif staff.role == "DELIVERY":
            out_for_delivery = parcels.filter(status="OUT_FOR_DELIVERY").count()
            delivered = parcels.filter(status="DELIVERED").count()
            cancelled = parcels.filter(status="CANCELLED").count()

            response.update({
                "out_for_delivery": out_for_delivery,
                "delivered": delivered,
                "cancelled": cancelled
            })

        return Response(response) 

class HubParcelListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        staff = getattr(request.user, "staff", None)

        if not staff or staff.role != "HUB":
            return Response({"error": "Not hub staff"}, status=403)

        # 🔥 STAFF DISTRICT
        staff_loc = get_location_from_pincode(staff.pincode)
        staff_city = staff_loc.get("city") if staff_loc else None

        parcels = Parcel.objects.all()

        filtered = []

        for p in parcels:
            source_city = get_location_from_pincode(p.source_pincode).get("city")
            dest_city = get_location_from_pincode(p.destination_pincode).get("city")

            # 🔵 SOURCE HUB LOGIC
            if staff_city == source_city:
                if p.status in ["PICKED_UP", "ARRIVED_AT_SENDER_HUB"]:
                    filtered.append(p)

            # 🟢 DEST HUB LOGIC
            elif staff_city == dest_city:
                if p.status in ["IN_TRANSIT", "ARRIVED_AT_DESTINATION_HUB"]:
                    filtered.append(p)

        data = [
            {
                "parcel_id": p.id,
                "tracking_id": p.tracking_id,
                "status": p.status,
                "source": p.source_pincode,
                "destination": p.destination_pincode
            }
            for p in filtered
        ]

        return Response(data)

class CancelParcelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, parcel_id):
        try:
            parcel = Parcel.objects.get(id=parcel_id, user=request.user)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        # ❌ Already cancelled
        if parcel.status == "CANCELLED":
            return Response({"error": "Already cancelled"}, status=400)

        # ❌ Cannot cancel after pickup started
        last_tracking = parcel.tracking_history.last()

        if last_tracking and last_tracking.status != "CREATED":
            return Response({
                "error": "Cannot cancel after pickup started"
            }, status=400)

        # ✅ Cancel parcel
        parcel.status = "CANCELLED"
        parcel.save()

        # 🔥 OPTIONAL: ADD TRACKING ENTRY
        location_data = get_location_from_pincode(parcel.source_pincode)

        if location_data:
            location_obj = Location.objects.create(
                name=location_data.get("name", "Unknown"),
                pincode=parcel.source_pincode,
                city=location_data.get("city", "Unknown"),
                state=location_data.get("state", "Unknown")
            )
        else:
            location_obj = Location.objects.create(
                name="Unknown",
                pincode=parcel.source_pincode,
                city="Unknown",
                state="Unknown"
            )

        Tracking.objects.create(
            parcel=parcel,
            location=location_obj,
            status="CANCELLED",
            note="Cancelled by user"
        )

        return Response({
            "message": "Parcel cancelled successfully"
        })

# 🔥 GET PICKUP REQUESTS
class PickupRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        staff = getattr(request.user, "staff", None)

        if not staff or staff.role != "PICKUP":
            return Response({"error": "Not pickup staff"}, status=403)

        # 🔥 GET STAFF DISTRICT
        staff_loc = get_location_from_pincode(staff.pincode)
        staff_city = staff_loc.get("city") if staff_loc else None

        parcels = Parcel.objects.filter(
            status="CONFIRMED",
            assigned_staff__isnull=True
        )

        filtered = []

        for p in parcels:
            parcel_loc = get_location_from_pincode(p.source_pincode)
            parcel_city = parcel_loc.get("city") if parcel_loc else None

            # 🔥 MATCH DISTRICT (CITY)
            if parcel_city == staff_city:
                filtered.append({
                    "parcel_id": p.id,
                    "tracking_id": p.tracking_id,
                    "sender": p.sender_name,
                    "pincode": p.source_pincode
                })

        return Response(filtered)

# 🔥 ACCEPT PICKUP
class AcceptPickupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, parcel_id):
        try:
            staff = request.user.staff
        except:
            return Response({"error": "Not staff"}, status=403)

        if staff.role != "PICKUP":
            return Response({"error": "Not pickup staff"}, status=403)

        try:
            parcel = Parcel.objects.get(id=parcel_id)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        # 🔥 FIRST ACCEPT WINS
        if parcel.status != "CONFIRMED" or parcel.assigned_staff:
            return Response({"error": "Already taken"}, status=400)

        parcel.assigned_staff = staff
        parcel.save()

        return Response({"message": "Pickup accepted"})


class MyPickupParcelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        staff = getattr(request.user, "staff", None)

        if not staff or staff.role != "PICKUP":
            return Response({"error": "Not pickup staff"}, status=403)

        parcels = Parcel.objects.filter(
            assigned_staff=staff
        ).order_by('-created_at')  # 🔥 latest first

        data = []

        for p in parcels:
            data.append({
                "parcel_id": p.id,
                "tracking_id": p.tracking_id,
                "status": p.status,
                "source_pincode": p.source_pincode,
                "destination_pincode": p.destination_pincode,
                "is_cancelled": p.status == "CANCELLED"
            })

        return Response(data)



class DeliveryRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        staff = getattr(request.user, "staff", None)

        if not staff or staff.role != "DELIVERY":
            return Response({"error": "Not delivery staff"}, status=403)

        # 🔥 STAFF DISTRICT
        staff_loc = get_location_from_pincode(staff.pincode)
        staff_city = staff_loc.get("city") if staff_loc else None

        parcels = Parcel.objects.filter(
            status="ARRIVED_AT_DESTINATION_HUB",
            assigned_delivery_staff__isnull=True
        )

        filtered = []

        for p in parcels:
            dest_loc = get_location_from_pincode(p.destination_pincode)
            dest_city = dest_loc.get("city") if dest_loc else None

            if dest_city == staff_city:
                filtered.append({
                    "parcel_id": p.id,
                    "tracking_id": p.tracking_id,
                    "receiver": p.receiver_name,
                    "pincode": p.destination_pincode
                })

        return Response(filtered)

class AcceptDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, parcel_id):
        staff = getattr(request.user, "staff", None)

        if not staff or staff.role != "DELIVERY":
            return Response({"error": "Not delivery staff"}, status=403)

        try:
            parcel = Parcel.objects.get(id=parcel_id)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        # 🔥 FIRST ACCEPT WINS
        if parcel.status != "ARRIVED_AT_DESTINATION_HUB" or parcel.assigned_delivery_staff:
            return Response({"error": "Already taken"}, status=400)

        parcel.assigned_delivery_staff = staff
        parcel.status = "OUT_FOR_DELIVERY"
        parcel.save()

        return Response({"message": "Delivery accepted"})

class MyDeliveryParcelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        staff = getattr(request.user, "staff", None)

        if not staff or staff.role != "DELIVERY":
            return Response({"error": "Not delivery staff"}, status=403)

        parcels = Parcel.objects.filter(
            assigned_delivery_staff=staff
        ).order_by('-created_at')

        data = []

        for p in parcels:
            data.append({
                "parcel_id": p.id,
                "tracking_id": p.tracking_id,
                "status": p.status,
                "destination_pincode": p.destination_pincode,
                "is_cancelled": p.status == "CANCELLED"
            })

        return Response(data)