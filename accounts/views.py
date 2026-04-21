from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.db.models import Sum

from parcel.models import Parcel
from .models import Staff


# 🔐 SIGNUP
class SignupView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response({"error": "All fields are required"}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        return Response({"message": "User created successfully"}, status=201)


# 🔐 LOGOUT
class LogoutView(APIView):
    def post(self, request):
        return Response({"message": "Logout handled on frontend"})


# 👨‍💼 CREATE STAFF (FIXED)
class CreateStaffView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role")
        pincode = request.data.get("pincode")

        if not email or not password or not role or not pincode:
            return Response({"error": "All fields required"}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email"}, status=400)

        if User.objects.filter(username=email).exists():
            return Response({"error": "User already exists"}, status=400)

        # 🔥 Create User
        user = User.objects.create(
            username=email,
            email=email,
            password=make_password(password),
            is_staff=True
        )

        # 🔥 Create Staff Profile (IMPORTANT)
        staff = Staff.objects.create(
            user=user,
            role=role,
            pincode=pincode
        )

        # 📧 Send Email
        send_mail(
            subject="You are hired!",
            message=f"""
Hello,

You are assigned as {role}.

Login:
Email: {email}
Password: {password}
""",
            from_email="yourgmail@gmail.com",
            recipient_list=[email],
            fail_silently=False
        )

        return Response({
            "message": "Staff created",
            "staff_id": staff.id
        }, status=201)


# ❌ DELETE STAFF (FIXED)
class DeleteStaffView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, staff_id):
        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            return Response({"error": "Staff not found"}, status=404)

        user = staff.user
        email = user.email

        staff.is_active = False
        staff.save()

        user.is_active = False
        user.save()

        send_mail(
            subject="Account Terminated",
            message="Your staff account has been removed.",
            from_email="yourgmail@gmail.com",
            recipient_list=[email],
            fail_silently=False
        )

        return Response({"message": "Staff terminated"})


# 📋 STAFF LIST (FIXED — SHOW ROLE)
class StaffListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        staff = Staff.objects.select_related("user").all()

        data = []
        for s in staff:
            data.append({
                "staff_id": s.id,
                "user_id": s.user.id,
                "email": s.user.email,
                "role": s.role,
                "pincode": s.pincode,
                "is_active": s.is_active
            })

        return Response(data)


# 👥 USER LIST
class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_staff=False).values(
            "id", "username", "email"
        )
        return Response(list(users))


# 👤 USER DETAIL + HISTORY
class UserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, is_staff=False)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        parcels = Parcel.objects.filter(user=user).values()

        return Response({
            "user": {
                "id": user.id,
                "email": user.email
            },
            "parcel_history": list(parcels)
        })


# 📦 PARCEL LIST
class ParcelListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(list(Parcel.objects.all().values()))


# 📊 DASHBOARD
class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_sales = Parcel.objects.filter(is_confirmed=True).aggregate(
            total=Sum("price")
        )

        return Response({
            "total_sales": total_sales["total"] or 0,
            "total_parcels": Parcel.objects.count()
        })