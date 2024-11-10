from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import FormLink, Subject, Institute, Lesson, StudentFeedback

User = get_user_model()

class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = ["id", "name", "rating"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'surname', 'last_name', 'institute']


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
    

class FormLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormLink
        fields = ['token', 'created_at', 'expires_at', 'is_active']
        
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id","name", "teacher_id"]


class LessonSerializer(serializers.ModelSerializer):
    unique_link = serializers.SerializerMethodField()
    is_link_active = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'teacher', 'institute', 'subject', 'topic', 'location',
            'start_time', 'end_time', 'unique_code', 'unique_link',
            'is_active', 'activation_duration', 'is_link_active',
        ]
        read_only_fields = ['unique_code', 'unique_link', 'is_link_active']

    def get_unique_link(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_unique_link())
        return obj.get_unique_link()

    def get_is_link_active(self, obj):
        return obj.is_link_active()
    
class StudentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeedback
        fields = ['id', 'lesson', 'student_name', 'rating', 'comment', 'praises', 'created_at']
        read_only_fields = ['created_at']