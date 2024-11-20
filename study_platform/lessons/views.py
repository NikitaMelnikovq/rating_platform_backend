import io
import base64
from datetime import timedelta

from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
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
        lesson = serializer.save(teacher=self.request.user)
        # После создания урока генерируем QR-код
        # Получаем URL для обратной связи
        feedback_url = self.request.build_absolute_uri(
            reverse('lessons:student-feedback', kwargs={'unique_code': lesson.unique_code})
        )

        # Генерируем QR-код
        img = qrcode.make(feedback_url)
        # Сохраняем QR-код в память
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        # Кодируем изображение в base64
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        # Сохраняем QR-код в экземпляр урока (если нужно)
        lesson.qr_code_base64 = qr_code_base64
        lesson.save()
        # Сохраняем QR-код для использования в ответе
        self.qr_code_base64 = qr_code_base64

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Добавляем QR-код в ответ
        response.data['qr_code'] = self.qr_code_base64
        return response
    

class LessonDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, unique_code):
        try:
            lesson = Lesson.objects.get(unique_code=unique_code, teacher=request.user)
            lesson.delete()
            return Response({"message": "Lesson deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Lesson.DoesNotExist:
            return Response({"error": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)


class LessonDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    lookup_field = 'unique_code'

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
    
# lessons/views.py
class StudentFeedbackCreateView(generics.CreateAPIView):
    serializer_class = StudentFeedbackSerializer

    def create(self, request, *args, **kwargs):
        lesson_code = kwargs.get('unique_code')
        try:
            lesson = Lesson.objects.get(unique_code=lesson_code)
            if not lesson.is_link_active():
                return Response({'error': 'Link is not active'}, status=status.HTTP_400_BAD_REQUEST)
            # Associate the feedback with the lesson
            request.data['lesson'] = lesson.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Lesson.DoesNotExist:
            return Response({'error': 'Invalid lesson code'}, status=status.HTTP_404_NOT_FOUND)


class IncreaseTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, unique_code):
        try:
            # Find the lesson by unique_code
            lesson = Lesson.objects.get(unique_code=unique_code, teacher=request.user)

            # Increase the activation duration by 10 minutes
            lesson.activation_duration += timedelta(minutes=10)
            lesson.end_time += timedelta(minutes=10)
            lesson.save()

            return Response(
                {"message": "Activation duration increased by 10 minutes."},
                status=status.HTTP_200_OK,
            )
        except Lesson.DoesNotExist:
            return Response(
                {"error": "Lesson not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )
        

def generate_qr_code(request, unique_code):
    lesson = get_object_or_404(Lesson, unique_code=unique_code)
    frontend_base_url = "http://localhost:5173"  
    url = f"{frontend_base_url}/form/{lesson.unique_code}/"
    img = qrcode.make(url)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response