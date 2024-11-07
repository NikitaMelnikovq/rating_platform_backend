from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    AdminOnlyView, 
    TeacherOnlyView, 
    UpdateProfileView, 
    ChangePasswordView, 
    UserListView, 
    UserInfoView, 
    GenerateLinkView, 
    ValidateLinkView, 
    ToggleLinkView,
    SubjectDeleteView, 
    SubjectListCreateView,
    TeacherSubjectListView
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', AdminOnlyView.as_view(), name='admin-only'),
    path('teacher/', TeacherOnlyView.as_view(), name='teacher-only'),
    path('api/user-info/',  UserInfoView.as_view(), name='user-info'),
    path('api/update-profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/subjects/', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('api/subjects/<int:pk>/', SubjectDeleteView.as_view(), name='subject-delete'),
    path('generate-link/', GenerateLinkView.as_view(), name='generate-link'),
    path('validate-link/<uuid:token>/', ValidateLinkView.as_view(), name='validate-link'),
    path('toggle-link/<uuid:token>/', ToggleLinkView.as_view(), name='toggle-link'),
    path('api/teacher-subjects/', TeacherSubjectListView.as_view(), name='teacher-subjects'),
]


app_name = 'app'