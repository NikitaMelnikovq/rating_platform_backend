from django.urls import path

from .views import (
    LessonByCodeView,
    LessonCreateView,
    LessonDetailView,
    TeacherLessonListView,
    StudentFeedbackCreateView,
    LessonDeleteView,
    IncreaseTimeView,
    LessonStatView,
    TeacherLessonListByIdView,
    TeacherExcelReportView,
    generate_qr_code,
)

app_name = 'lessons' 

urlpatterns = [
    path('', LessonCreateView.as_view(), name='lesson-create'),
    path('<uuid:unique_code>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('subjects/', TeacherLessonListView.as_view(), name='teacher-lessons-list'),
    path('code/<uuid:unique_code>/', LessonByCodeView.as_view(), name='lesson-by-code'),
    path('<uuid:unique_code>/delete/', LessonDeleteView.as_view(), name='lesson-delete'),
    path('code/<uuid:unique_code>/feedback/', StudentFeedbackCreateView.as_view(), name='student-feedback'),
    path('code/<uuid:unique_code>/qr/', generate_qr_code, name='generate-qr-code'),
    path('<uuid:unique_code>/increase-time/', IncreaseTimeView.as_view(), name='increase-time'),
    path('<uuid:unique_code>/lesson-stat/', LessonStatView.as_view(), name='increase-time'),
    path('teacher-lessons/<int:id>/', TeacherLessonListByIdView.as_view(), name='teacher-lessons-by-id'),   
    path("teacher-report/<int:id>/", TeacherExcelReportView.as_view(), name="teacher-report"),
]
