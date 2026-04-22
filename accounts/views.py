from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status

from django.contrib.auth.models import User
from django.db.models import Sum

from .models import Staff
from .serializers import (
    UserSerializer,
    StaffSerializer,
    TrackingSerializer
)

# ✅ CORRECT IMPORT
from parcel.serializers import ParcelSerializer
from parcel.models import Parcel
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


# 👨‍💼 CREATE STAFF
class CreateStaffView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = StaffSerializer(data=request.data)

        if serializer.is_valid():
            staff = serializer.save()
            return Response({
                "message": "Staff created",
                "staff_id": staff.id
            }, status=201)

        return Response(serializer.errors, status=400)


# ❌ DELETE STAFF
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

        return Response({"message": "Staff terminated"})


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


# 📦 CREATE PARCEL (🔥 VERY IMPORTANT FIX)
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


# 📦 PARCEL DETAIL + HISTORY
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