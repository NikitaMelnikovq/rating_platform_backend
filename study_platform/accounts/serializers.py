from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import User


class UserSerializer(serializers.ModelSerializer):

    rating = serializers.FloatField(default=0.0, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role',
            'first_name',
            'surname',
            'last_name',
            'institute',
            "rating",
            "password"
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            institute=validated_data["institute"],
            first_name=validated_data["first_name"],
            last_name=validated_data.get("last_name", ''),
            surname=validated_data["surname"],
            role=validated_data["role"],
            rating=0,
        )

        return user
    

class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role',
            'first_name',
            'surname',
            'last_name',
            'institute',
            'rating',
            'password',
            "is_active",
            "visible_reviews"
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.role = validated_data.get('role', instance.role)
        instance.institute = validated_data.get('institute', instance.institute)
        instance.username = validated_data.get('username', instance.username)
        instance.is_active = validated_data.get('is_active', instance.username)
        instance.visible_reviews = validated_data.get('visible_reviews', instance.visible_reviews)

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)

        instance.save()
        return instance


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
            raise serializers.ValidationError(
                "Пользователь с таким логином уже существует.")
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
