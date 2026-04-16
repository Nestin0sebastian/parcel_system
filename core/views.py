from urllib import response

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Application
from .serializers import ApplicationSerializer, UserSerializer


# 🔹 APPLY JOB API
class   ApplyJobView(APIView):

    def post(self, request):
        serializer = ApplicationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Application submitted successfully",
                "data": serializer.data
            })

        return Response(serializer.errors)


# 🔹 SIGNUP API
class SignupView(APIView):

    def post(self,request):
        serializer=UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({


           "message":"User created Successfully",
            "data":serializer.data
            })


# 🔹 LOGIN API
class LoginView(APIView):

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            return Response({
                "message": "Login successful",
                "user_id": user.id
            })
        else:
            return Response({
                "error": "Invalid username or password"
            })
        