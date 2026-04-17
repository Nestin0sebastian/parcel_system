from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate

from .models import User
from .serializers import UserSerializer


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