from django.urls import path

from .views import InstituteListView

urlpatterns = [
    path('', InstituteListView.as_view(), name='institute-list')
]
