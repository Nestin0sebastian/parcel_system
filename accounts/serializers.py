from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Staff
from parcel.models import Parcel
from tracking.models import Tracking


# 🔐 USER SERIALIZER (SIGNUP)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


# 👨‍💼 STAFF SERIALIZER
class StaffSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'email', 'password', 'role', 'pincode', 'is_active']

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # ❌ prevent duplicate users
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError("User already exists")

        # 🔥 create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_staff=True
        )

        # 🔥 create staff
        staff = Staff.objects.create(user=user, **validated_data)
        return staff

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['username'] = instance.user.username
        return data


# 📦 PARCEL SERIALIZER (BASIC)
class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = '__all__'
        read_only_fields = [
            'tracking_id',
            'price',
            'status',
            'is_confirmed',
            'otp',
            'otp_verified',
            'assigned_delivery_staff',
            'created_at'
        ]


# 📍 TRACKING SERIALIZER
class TrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracking
        fields = '__all__'