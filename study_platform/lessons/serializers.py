from rest_framework import serializers
from django.utils import timezone

from .models import (
    Lesson,
    FormLink,
    StudentFeedback,
)
from institute.models import Institute
from accounts.models import User


class LessonSerializer(serializers.ModelSerializer):
    unique_link = serializers.SerializerMethodField()
    is_link_active = serializers.SerializerMethodField()
    student_feedback_count = serializers.SerializerMethodField()
    student_feedback = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'teacher', 'institute', 'subject', 'topic', 'location',
            'start_time', 'end_time', 'unique_code', 'unique_link',
            'is_active', 'is_link_active', 'qr_code_base64', 'average_rating',
            'student_feedback_count', 'student_feedback'
        ]
        read_only_fields = ['unique_code', 'unique_link', 'is_link_active']

    def get_unique_link(self, obj):
        frontend_base_url = 'http://localhost:5173'
        return f'{frontend_base_url}/form/{obj.unique_code}/'

    def get_is_link_active(self, obj):
        return obj.is_link_active()

    def get_student_feedback_count(self, obj):
        return StudentFeedback.objects.filter(lesson=obj).count()

    def get_student_feedback(self, obj):
        request = self.context.get('request')
        if not request:
            return []

        user = request.user
        if not isinstance(user, User) or not user.visible_reviews:
            return []

        feedbacks = StudentFeedback.objects.filter(lesson=obj)
        return [
            {
                'rating': feedback.rating,
                'comment': feedback.comment,
                'praises': feedback.praises,
                'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for feedback in feedbacks
        ]

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        topic = data.get('topic')

        if end_time <= start_time:
            raise serializers.ValidationError(
                'Время окончания должно быть больше времени начала.'
            )
        if start_time.year > timezone.now().year:
            raise serializers.ValidationError(
                'Год не может быть больше текущего.'
            )
        if len(topic) > 250:
            raise serializers.ValidationError('Максимальная длина темы — 250 символов.')

        return data

    def create(self, validated_data):
        return super().create(validated_data)


class FormLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormLink
        fields = ['token', 'created_at', 'expires_at', 'is_active']


class TeacherShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'surname']


class InstituteShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = ['id', 'name']


class LessonShortSerializer(serializers.ModelSerializer):
    teacher = TeacherShortSerializer(read_only=True)
    institute = InstituteShortSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'topic', 'location', 'teacher', 'institute']


class StudentFeedbackSerializer(serializers.ModelSerializer):
    lesson = LessonShortSerializer(read_only=True)

    class Meta:
        model = StudentFeedback
        fields = [
            'id', 'lesson', 'student_name',
            'rating', 'comment', 'praises', 'created_at'
        ]
        read_only_fields = ['created_at']
