from django.contrib.auth import get_user_model
from rest_framework import (
    generics,
    status,
    filters,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.permissions import IsAdminUser, IsTeacherUser
from .serializers import (
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserListSerializer,
)

User = get_user_model()

# Create your views here.
class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]


class TeacherOnlyView(APIView):
    permission_classes = [IsTeacherUser]


class UserInfoView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    

class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.userUser



class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
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
    

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'surname']


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer