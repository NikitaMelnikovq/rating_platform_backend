from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import User


class UserSerializer(serializers.ModelSerializer):

    rating = serializers.FloatField(default=0.0, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'first_name', 'surname', 'last_name', 'institute', "rating"]


    def create(self, validated_data):
        full_name = validated_data["name"]

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            institute=validated_data["institute"],
            role=validated_data["role"],
            
            rating=0,
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(default=0.0, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'surname', 'rating']

        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'surname': {'required': False, 'allow_blank': True},
        }

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким логином уже существует.")
        return value
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value, self.context['request'].user)
        return value
    

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'surname', 'role', 'rating']