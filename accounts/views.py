# 🔹 DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated

# 🔹 Django
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

# 🔹 Python
from django.utils import timezone

from datetime import timedelta
import random

# 🔹 Local Apps
from .models import Staff
from .serializers import UserSerializer, StaffSerializer, TrackingSerializer

# 🔹 Other Apps
from parcel.models import Parcel
from parcel.serializers import ParcelSerializer
from tracking.models import Tracking

# 🔐 SIGNUP
class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created"}, status=201)

        return Response(serializer.errors, status=400)


# 🔐 LOGOUT
class LogoutView(APIView):
    def post(self, request):
        return Response({"message": "Logout handled on frontend"})


# 👨‍💼 CREATE STAFF + EMAIL
from django.core.mail import send_mail
from django.conf import settings


class CreateStaffView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = StaffSerializer(data=request.data)

        if serializer.is_valid():
            # 👉 Get password BEFORE saving (important)
            raw_password = request.data.get("password")

            staff = serializer.save()

            # 📧 EMAIL SEND (with password)
            send_mail(
                subject="Staff Account Created",
                message=f"""
Hello,

Your staff account has been created successfully.

🔐 Login Details:
Email: {staff.user.email}
Password: {raw_password}

Role: {staff.role}

👉 Please login and change your password after first login.

🚚 Welcome to the system!
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[staff.user.email],
                fail_silently=True,
            )

            return Response({
                "message": "Staff created & email sent",
                "staff_id": staff.id
            }, status=201)

        return Response(serializer.errors, status=400)
    



# ❌ DELETE STAFF + EMAIL
class DeleteStaffView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, staff_id):
        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            return Response({"error": "Staff not found"}, status=404)

        staff.user.is_active = False
        staff.user.save()

        staff.is_active = False
        staff.save()

        # 📧 EMAIL SEND
        send_mail(
            subject="Account Deactivated",
            message="Your staff account has been deactivated.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[staff.user.email],
            fail_silently=True,
        )

        return Response({"message": "Staff terminated & email sent"})


# 📋 STAFF LIST
class StaffListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        staff = Staff.objects.all()
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)


# 👥 USER LIST
class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_staff=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# 👤 USER DETAIL
class UserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, is_staff=False)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        parcels = Parcel.objects.filter(user=user)
        serializer = ParcelSerializer(parcels, many=True)

        return Response({
            "user": {
                "id": user.id,
                "email": user.email
            },
            "parcel_history": serializer.data
        })


# 📦 PARCEL LIST
class ParcelListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        parcels = Parcel.objects.all()
        serializer = ParcelSerializer(parcels, many=True)
        return Response(serializer.data)


# 📊 ADMIN DASHBOARD
class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_sales = Parcel.objects.aggregate(total=Sum("price"))

        return Response({
            "total_sales": total_sales["total"] or 0,
            "total_parcels": Parcel.objects.count()
        })


# 📦 CREATE PARCEL
class CreateParcelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ParcelSerializer(data=request.data)

        if serializer.is_valid():
            parcel = serializer.save(user=request.user)

            return Response({
                "message": "Parcel created successfully",
                "parcel_id": parcel.id,
                "price": parcel.price
            }, status=201)

        return Response(serializer.errors, status=400)


# 📦 PARCEL DETAIL + TRACKING
class ParcelDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcel_id):
        try:
            parcel = Parcel.objects.get(id=parcel_id)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        parcel_data = ParcelSerializer(parcel).data

        history = Tracking.objects.filter(parcel=parcel).order_by("timestamp")
        history_data = TrackingSerializer(history, many=True).data

        return Response({
            "parcel": parcel_data,
            "history": history_data
        })

class AcceptDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, parcel_id):
        user = request.user

        if not hasattr(user, "staff") or user.staff.role != "DELIVERY":
            return Response({"error": "Only delivery staff allowed"}, status=403)

        try:
            parcel = Parcel.objects.get(id=parcel_id)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        # 🔥 NEW FLOW
        if parcel.status != "ARRIVED_AT_DESTINATION_HUB":
            return Response({
                "error": "Parcel not ready for delivery",
                "current_status": parcel.status
            }, status=400)

        if parcel.assigned_delivery_staff:
            return Response({"error": "Already assigned"}, status=400)

        # ✅ Assign + move to delivery
        parcel.assigned_delivery_staff = user.staff
        parcel.status = "OUT_FOR_DELIVERY"
        parcel.save()

        return Response({
            "message": "Delivery accepted successfully"
        })


class GenerateOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, parcel_id):
        user = request.user

        if not hasattr(user, "staff") or user.staff.role != "DELIVERY":
            return Response({"error": "Only delivery staff allowed"}, status=403)

        try:
            parcel = Parcel.objects.get(id=parcel_id)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        if parcel.assigned_delivery_staff != user.staff:
            return Response({"error": "Not your parcel"}, status=403)

        if parcel.status != "OUT_FOR_DELIVERY":
            return Response({"error": "Invalid status"}, status=400)

        # 🔥 Cooldown (1 min)
        if parcel.otp_created_at:
            if timezone.now() < parcel.otp_created_at + timedelta(minutes=1):
                return Response({
                    "error": "OTP already generated. Try after 1 minute"
                }, status=400)

        # 🔐 Generate OTP
        otp = str(random.randint(100000, 999999))
        parcel.otp = otp
        parcel.otp_created_at = timezone.now()
        parcel.save()

        # 📧 Send Email
        send_mail(
            subject="Your Delivery OTP",
            message=f"Your OTP is {otp}. Valid for 5 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[parcel.receiver_email],
            fail_silently=False,
        )

        return Response({
            "message": "OTP generated and sent"
        })
    

class DeliverParcelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, parcel_id):
        user = request.user
        otp_input = request.data.get("otp")

        if not hasattr(user, "staff") or user.staff.role != "DELIVERY":
            return Response({"error": "Only delivery staff allowed"}, status=403)

        try:
            parcel = Parcel.objects.get(id=parcel_id)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        if parcel.assigned_delivery_staff != user.staff:
            return Response({"error": "Not your parcel"}, status=403)

        if parcel.status != "OUT_FOR_DELIVERY":
            return Response({"error": "Invalid status"}, status=400)

        if not otp_input:
            return Response({"error": "OTP required"}, status=400)

        if not parcel.otp or not parcel.otp_created_at:
            return Response({"error": "OTP not generated"}, status=400)

        # ⏳ Expiry (5 min)
        if timezone.now() > parcel.otp_created_at + timedelta(minutes=5):
            return Response({"error": "OTP expired"}, status=400)

        if parcel.otp != otp_input:
            return Response({"error": "Invalid OTP"}, status=400)

        # ✅ SUCCESS
        parcel.status = "DELIVERED"
        parcel.otp_verified = True
        parcel.otp = None
        parcel.save()

        return Response({"message": "Delivered successfully"})    

