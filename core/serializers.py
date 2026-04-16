from rest_framework import serializers
from .models import Application, Job
from django.contrib.auth.models import User


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'        