from django.urls import path
from .views import user_info
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import AdminOnlyView, TeacherOnlyView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', AdminOnlyView.as_view(), name='admin-only'),
    path('teacher/', TeacherOnlyView.as_view(), name='teacher-only'),
    path('api/user-info/', user_info, name='user-info'),
]

app_name = 'app'