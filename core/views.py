from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate

from .models import User, Parcel, Tracking
from .serializers import UserSerializer, ParcelSerializer, TrackingSerializer


# 🔹 SIGNUP API
class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User created successfully",
                "data": serializer.data
            })

        return Response(serializer.errors)


# 🔹 LOGIN API
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = User.objects.filter(username=username, password=password).first()

        if user:
            return Response({
                "message": "Login successful",
                "user_id": user.id,
                "role": user.role
            })

        return Response({
            "error": "Invalid username or password"
        })


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