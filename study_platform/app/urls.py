from django.urls import path, include

urlpatterns = [
    path("api/accounts/", include("accounts.urls")),
    path("api/subjects/", include("subjects.urls")),
    path("api/lessons/", include("lessons.urls")),
    path("api/institutes/", include("institute.urls")),
    
]


app_name = 'app'