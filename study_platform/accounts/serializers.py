from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'surname', 'last_name', 'institute', "rating"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'surname']

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
    rating = serializers.SerializerMethodField()
    role = serializers.CharField(source='get_role_display')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'surname', 'role', 'rating']

    def get_rating(self, obj):
        # Предположим, что у пользователей есть поле rating или метод для его вычисления
        # Если это не так, замените реализацию на вашу
        return obj.get_rating() if hasattr(obj, 'get_rating') else None