from django.shortcuts import get_object_or_404
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated

from .serializers import SubjectSerializer
from .models import Subject
from app.permissions import IsTeacherUser


class SubjectListCreateView(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def get_queryset(self):
        return Subject.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class SubjectDeleteView(generics.DestroyAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsTeacherUser]
    queryset = Subject.objects.all()

    def get_object(self):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'], teacher_id=self.request.user)
        return subject
    
class TeacherSubjectListView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsTeacherUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        return Subject.objects.filter(teacher_id=self.request.user)