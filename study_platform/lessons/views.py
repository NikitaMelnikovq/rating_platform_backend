from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, filters, status
from rest_framework.response import Response
import qrcode 

from .serializers import LessonSerializer, StudentFeedbackSerializer
from .models import Lesson
# Create your views here.

class LessonCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class LessonDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        return Lesson.objects.filter(teacher=self.request.user)

    def patch(self, request, *args, **kwargs):
        # Handle QR code generation or activation changes
        return self.partial_update(request, *args, **kwargs)


class LessonByCodeView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    lookup_field = 'unique_code'
    queryset = Lesson.objects.all()

    def get(self, request, *args, **kwargs):
        lesson = self.get_object()
        if not lesson.is_link_active():
            return Response({'error': 'Link is not active'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(lesson)
        return Response(serializer.data)

class TeacherLessonListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['start_time', 'end_time']
    search_fields = ['topic']

    def get_queryset(self):
        return Lesson.objects.filter(teacher=self.request.user)
    
class StudentFeedbackCreateView(generics.CreateAPIView):
    serializer_class = StudentFeedbackSerializer

    def create(self, request, *args, **kwargs):
        lesson_code = kwargs.get('unique_code')
        try:
            lesson = Lesson.objects.get(unique_code=lesson_code)
            if not lesson.is_link_active():
                return Response({'error': 'Link is not active'}, status=status.HTTP_400_BAD_REQUEST)
            request.data['lesson'] = lesson.id
            return super().create(request, *args, **kwargs)
        except Lesson.DoesNotExist:
            return Response({'error': 'Invalid lesson code'}, status=status.HTTP_404_NOT_FOUND)
    
def generate_qr_code(request, unique_code):
    lesson = get_object_or_404(Lesson, unique_code=unique_code)
    url = request.build_absolute_uri(lesson.get_unique_link())
    img = qrcode.make(url)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response