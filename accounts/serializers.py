from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Staff
from parcel.models import Parcel
from tracking.models import Tracking


# 🔐 USER (SIGNUP)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)


# 👨‍💼 STAFF
class StaffSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'email', 'password', 'role', 'pincode', 'is_active']

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        user = User.objects.create(
            username=email,
            email=email,
            password=make_password(password),
            is_staff=True
        )

        staff = Staff.objects.create(user=user, **validated_data)
        return staff





# 📍 TRACKING
class TrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracking
        fields = '__all__'