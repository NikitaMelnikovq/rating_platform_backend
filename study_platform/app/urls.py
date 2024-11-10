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
    TeacherSubjectListView,
    CurrentUserView,
    InstituteListView,
    LessonCreateView,
    LessonDetailView,
    LessonByCodeView,
    StudentFeedbackCreateView,
    TeacherLessonListView
)
from .views import generate_qr_code

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
    path('api/current-user/', CurrentUserView.as_view(), name='current-user'),
    path('api/institutes/', InstituteListView.as_view(), name='institute-list'),
    path('api/lessons/', LessonCreateView.as_view(), name='lesson-create'),
    path('api/lessons/<int:id>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('api/lessons/code/<uuid:unique_code>/', LessonByCodeView.as_view(), name='lesson-by-code'),
    path('api/lessons/code/<uuid:unique_code>/feedback/', StudentFeedbackCreateView.as_view(), name='student-feedback'),
    path('api/lessons/code/<uuid:unique_code>/qr/', generate_qr_code, name='generate-qr-code'),
    path('api/lessons/subjects/', TeacherLessonListView.as_view(), name='teacher-lessons-list'),
]


app_name = 'app'