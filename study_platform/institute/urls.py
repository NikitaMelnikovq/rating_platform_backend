from django.urls import path

from .views import InstituteListView


app_name = "institute"

urlpatterns = [
    path('', InstituteListView.as_view(), name='institute-list')
]
