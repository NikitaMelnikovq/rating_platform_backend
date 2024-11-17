from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AdminOnlyView,
    TeacherOnlyView,
    UserInfoView,
    UpdateProfileView,
    ChangePasswordView,
    UserListView,
    CurrentUserView
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', AdminOnlyView.as_view(), name='admin-only'),
    path('teacher/', TeacherOnlyView.as_view(), name='teacher-only'),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('current-user/', CurrentUserView.as_view(), name='current-user'),
]