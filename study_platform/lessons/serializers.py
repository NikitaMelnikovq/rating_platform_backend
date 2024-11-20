from rest_framework import serializers
from django.utils import timezone

from .models import (
    Lesson,
    FormLink,
    StudentFeedback,
)


class LessonSerializer(serializers.ModelSerializer):
    unique_link = serializers.SerializerMethodField()
    is_link_active = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'teacher', 'institute', 'subject', 'topic', 'location',
            'start_time', 'end_time', 'unique_code', 'unique_link',
            'is_active', 'activation_duration', 'is_link_active', 'qr_code_base64'
        ]
        read_only_fields = ['unique_code', 'unique_link', 'is_link_active']

    def get_unique_link(self, obj):
        frontend_base_url = "http://localhost:5173" 
        return f"{frontend_base_url}/form/{obj.unique_code}/"
    
    def get_is_link_active(self, obj):
        return obj.is_link_active()
    
    
    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        topic = data.get('topic')

        # Проверка времени начала и окончания
        if end_time <= start_time:
            raise serializers.ValidationError("Время окончания должно быть больше времени начала.")

        # Проверка года
        if start_time.year > timezone.now().year:
            raise serializers.ValidationError("Год не может быть больше текущего.")

        # Проверка длины темы
        if len(topic) > 250:
            raise serializers.ValidationError("Максимальная длина темы — 250 символов.")

        return data
        
    def create(self, validated_data):
        start_time = validated_data['start_time']
        end_time = validated_data['end_time']
        duration = end_time - start_time
        validated_data['activation_duration'] = duration
        lesson = super().create(validated_data)
        return lesson

class FormLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormLink
        fields = ['token', 'created_at', 'expires_at', 'is_active']
    

class StudentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeedback
        fields = ['id', 'lesson', 'student_name', 'rating', 'comment', 'praises', 'created_at']
        read_only_fields = ['created_at']