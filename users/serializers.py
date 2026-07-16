# backend/users/serializers.py

from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    """
    Register  serializer
    password confirm 
    """
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'role']

    def validate(self, data):
        # all password matched
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match!")
        return data

    def create(self, validated_data):
        # password2 remove  — DB no enter in db
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'student')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Profile see update 
    
    """
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email',
            'role', 'bio', 'profile_picture', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']