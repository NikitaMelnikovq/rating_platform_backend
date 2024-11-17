from django.urls import path

from .views import (
    LessonByCodeView,
    LessonCreateView,
    LessonDetailView,
    TeacherLessonListView,
    StudentFeedbackCreateView,
    generate_qr_code
)

urlpatterns = [
    path('', LessonCreateView.as_view(), name='lesson-create'),
    path('<int:id>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('subjects/', TeacherLessonListView.as_view(), name='teacher-lessons-list'),
    path('code/<uuid:unique_code>/', LessonByCodeView.as_view(), name='lesson-by-code'),
    path('code/<uuid:unique_code>/feedback/', StudentFeedbackCreateView.as_view(), name='student-feedback'),
    path('code/<uuid:unique_code>/qr/', generate_qr_code, name='generate-qr-code'),
]