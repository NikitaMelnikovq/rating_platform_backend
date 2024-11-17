from rest_framework import serializers

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
    

class FormLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormLink
        fields = ['token', 'created_at', 'expires_at', 'is_active']
    

class StudentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeedback
        fields = ['id', 'lesson', 'student_name', 'rating', 'comment', 'praises', 'created_at']
        read_only_fields = ['created_at']