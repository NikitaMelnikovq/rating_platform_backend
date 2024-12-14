from django.urls import path

from .views import (
    SubjectListCreateView,
    SubjectDeleteView,
    TeacherSubjectListView,
    SubjectByTeacherView
)

urlpatterns = [
    path('', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('<int:pk>/', SubjectDeleteView.as_view(), name='subject-delete'),
    path('teacher-subjects/', TeacherSubjectListView.as_view(), name='teacher-subjects'),
    path("<int:teacher_id>/list", SubjectByTeacherView.as_view(), name="subjects-by-teacher"),
]