from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserPhoto, UserProfile


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = ['id', 'photo', 'is_main', 'uploaded_at']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'height', 'education', 'profession', 
                 'smoking', 'drinking', 'relationship_goals']


class UserSerializer(serializers.ModelSerializer):
    photos = UserPhotoSerializer(many=True, read_only=True)
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'gender', 
                 'age', 'city', 'hobbies', 'status', 'privacy_settings',
                 'likes_count', 'is_verified', 'photos', 'profile', 
                 'created_at']
        read_only_fields = ['likes_count', 'is_verified', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'gender', 'age', 
                 'city', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Создаем профиль пользователя
        UserProfile.objects.create(user=user)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'age', 'city', 
                 'hobbies', 'status', 'privacy_settings']