from django.urls import path, include

from .views import RatingSearchView, FilteredFeedbackListView, ReportExcelView

urlpatterns = [
    path('api/accounts/', include('accounts.urls')),
    path('api/subjects/', include('subjects.urls')),
    path('api/lessons/', include(('lessons.urls', 'lessons'), namespace='lessons')),
    path('api/institutes/', include('institute.urls')),
    path('api/rating/search/', RatingSearchView.as_view(), name='rating-search'),
    path('api/feedback/list/', FilteredFeedbackListView.as_view(), name='filtered-feedback-list'),
    path('api/report/excel/', ReportExcelView.as_view(), name='report-excel'),
]
