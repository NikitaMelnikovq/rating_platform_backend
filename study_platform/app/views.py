from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsAdminUser, IsTeacherUser
from .serializers import UserSerializer
from .serializers import UserUpdateSerializer
from .serializers import UserListSerializer
from .serializers import SubjectSerializer
from .serializers import InstituteSerializer
from .serializers import ChangePasswordSerializer
from .serializers import LessonSerializer, StudentFeedbackSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, filters
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .serializers import FormLinkSerializer
from .models import FormLink, Subject, Institute, Lesson
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
import qrcode
from django.http import HttpResponse

User = get_user_model()

class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"message": "Hello, Admin!"})

class TeacherOnlyView(APIView):
    permission_classes = [IsTeacherUser]

    def get(self, request):
        return Response({"message": "Hello, Teacher!"})
    
class UserInfoView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = request.user

            # Проверяем старый пароль
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Неверный пароль."]}, status=status.HTTP_400_BAD_REQUEST)

            # Устанавливаем новый пароль
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({"detail": "Пароль успешно изменен."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.userUser
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'surname']

class GenerateLinkView(APIView):
    permission_classes = [IsAuthenticated]  # Adjust permissions as needed

    def post(self, request):
        expires_in = request.data.get('expires_in')  # Expects duration in seconds
        expires_at = timezone.now() + timedelta(seconds=int(expires_in))
        form_link = FormLink.objects.create(expires_at=expires_at)
        serializer = FormLinkSerializer(form_link)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ValidateLinkView(APIView):
    def get(self, request, token):
        try:
            form_link = FormLink.objects.get(token=token)
            if form_link.is_valid():
                return Response({'message': 'Link is valid'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Link has expired or is inactive'}, status=status.HTTP_400_BAD_REQUEST)
        except FormLink.DoesNotExist:
            return Response({'message': 'Invalid link'}, status=status.HTTP_404_NOT_FOUND)
        
class ToggleLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, token):
        try:
            form_link = FormLink.objects.get(token=token)
            form_link.is_active = not form_link.is_active
            form_link.save()
            return Response({'is_active': form_link.is_active}, status=status.HTTP_200_OK)
        except FormLink.DoesNotExist:
            return Response({'message': 'Invalid link'}, status=status.HTTP_404_NOT_FOUND)
        
class SubjectListCreateView(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def get_queryset(self):
        # Возвращает предметы, связанные с текущим учителем
        return Subject.objects.filter(teacher_id=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher_id=self.request.user)


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
    
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class InstituteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        institutes = Institute.objects.all()
        serializer = InstituteSerializer(institutes, many=True)
        return Response(serializer.data)
    
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
    
def generate_qr_code(request, unique_code):
    lesson = get_object_or_404(Lesson, unique_code=unique_code)
    url = request.build_absolute_uri(lesson.get_unique_link())
    img = qrcode.make(url)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

class TeacherLessonListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['start_time', 'end_time']
    search_fields = ['topic']

    def get_queryset(self):
        return Lesson.objects.filter(teacher=self.request.user)