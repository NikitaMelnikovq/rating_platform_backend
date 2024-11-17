from rest_framework import serializers, generics, filters

from rest_framework.permissions import IsAuthenticated

from app.permissions import IsTeacherUser
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id","name", "teacher_id"]


class TeacherSubjectListView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsTeacherUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        return Subject.objects.filter(teacher_id=self.request.user)