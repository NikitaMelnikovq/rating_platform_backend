from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsAdminUser, IsTeacherUser
from .serializers import UserSerializer
from .serializers import UserUpdateSerializer
from .serializers import UserListSerializer
from .serializers import SubjectSerializer
from .serializers import ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, filters
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .serializers import FormLinkSerializer
from .models import FormLink, Subject
from django.shortcuts import get_object_or_404

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