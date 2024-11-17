from django.urls import path

from .views import (
    SubjectListCreateView,
    SubjectDeleteView,
    TeacherSubjectListView,
)

urlpatterns = [
    path('', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('<int:pk>/', SubjectDeleteView.as_view(), name='subject-delete'),
    path('teacher-subjects/', TeacherSubjectListView.as_view(), name='teacher-subjects'),
]