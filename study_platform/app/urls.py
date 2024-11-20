from django.urls import path, include

urlpatterns = [
    path("api/accounts/", include("accounts.urls")),
    path("api/subjects/", include("subjects.urls")),
    path("api/lessons/", include(('lessons.urls', 'lessons'), namespace='lessons')),
    path("api/institutes/", include("institute.urls")),
    
]
