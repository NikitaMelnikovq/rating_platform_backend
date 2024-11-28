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
from .tasks import process_feedback

class LessonCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        lesson = serializer.save(teacher=self.request.user)
        feedback_url = self.request.build_absolute_uri(
            reverse('lessons:student-feedback', kwargs={'unique_code': lesson.unique_code})
        )

        img = qrcode.make(feedback_url)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        lesson.qr_code_base64 = qr_code_base64
        lesson.save()
        self.qr_code_base64 = qr_code_base64

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data['qr_code'] = self.qr_code_base64
        return response
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})  # Передаем request в контекст
        return context

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})  # Передаем request в контекст
        return context

    def get_queryset(self):
        return Lesson.objects.filter(teacher=self.request.user)

    def patch(self, request, *args, **kwargs):
        # Handle QR code generation or activation changes
        return self.partial_update(request, *args, **kwargs)

class LessonStatView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})  # Передаем request в контекст
        return context

    def get_object(self):
        unique_code = self.kwargs.get("unique_code")

        return get_object_or_404(Lesson, unique_code=unique_code)




class LessonByCodeView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    lookup_field = 'unique_code'
    queryset = Lesson.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})  # Передаем request в контекст
        return context

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})  # Передаем request в контекст
        return context

    def get_queryset(self):
        return Lesson.objects.filter(teacher=self.request.user)
    


class StudentFeedbackCreateView(generics.CreateAPIView):
    serializer_class = StudentFeedbackSerializer

    def post(self, request, *args, **kwargs):
        lesson_code = kwargs.get('unique_code')
        try:
            lesson = Lesson.objects.get(unique_code=lesson_code)
            if not lesson.is_link_active():
                return Response({'error': 'Link is not active'}, status=status.HTTP_400_BAD_REQUEST)
            
            feedback_data = request.data.copy()
            feedback_data['lesson'] = lesson.id

            process_feedback.delay(feedback_data)

            return Response({'message': 'Feedback received and will be processed shortly.'}, status=status.HTTP_202_ACCEPTED)

        except Lesson.DoesNotExist:
            return Response({'error': 'Invalid lesson code'}, status=status.HTTP_404_NOT_FOUND)

class IncreaseTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, unique_code):
        try:
            lesson = Lesson.objects.get(unique_code=unique_code, teacher=request.user)

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