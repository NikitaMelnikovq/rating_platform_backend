from io import BytesIO

from rest_framework import generics
from django.db.models import Q
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import make_aware, get_current_timezone
from datetime import datetime, time
from openpyxl import Workbook
from django.http import HttpResponse

from subjects.models import Subject
from accounts.models import User
from lessons.models import Lesson, StudentFeedback
from institute.models import Institute
from lessons.serializers import StudentFeedbackSerializer
from .utils import (
        filter_feedbacks,
        generate_excel_report,
        get_entity_and_feedbacks,
        get_lesson_ratings,
        get_teacher_ratings,
    )

class RatingSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        institute_id = request.query_params.get('institute_id')
        teacher_id = request.query_params.get('teacher_id')
        subject_id = request.query_params.get('subject_id')

        data = {
            "rating": None,
            "top3": [],
            "bottom3": []
        }

        entity, entity_type, rating, _ = get_entity_and_feedbacks(
            institute_id, teacher_id, subject_id
        )
        data["rating"] = rating

        if entity_type == 'subject' and entity:
            top3, bottom3 = get_lesson_ratings(entity, {'subject': entity})
            data["top3"], data["bottom3"] = top3, bottom3

        elif entity_type == 'teacher' and entity:
            top3, bottom3 = get_lesson_ratings(entity, {'teacher': entity})
            data["top3"], data["bottom3"] = top3, bottom3

        elif entity_type == 'institute' and entity:
            top3, bottom3 = get_teacher_ratings(entity)
            data["top3"], data["bottom3"] = top3, bottom3

        return Response(data)
    

class FeedbackPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class FilteredFeedbackListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentFeedbackSerializer
    pagination_class = FeedbackPagination

    def get_queryset(self):
        institute_id = self.request.query_params.get('institute_id')
        teacher_id = self.request.query_params.get('teacher_id')
        subject_id = self.request.query_params.get('subject_id')
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')

        feedbacks = StudentFeedback.objects.all()

        if subject_id:
            feedbacks = feedbacks.filter(lesson__subject_id=subject_id)
        elif teacher_id:
            feedbacks = feedbacks.filter(lesson__teacher_id=teacher_id)
        elif institute_id:
            feedbacks = feedbacks.filter(lesson__institute_id=institute_id)

        if start_date_str:
            start_date = parse_date(start_date_str)
            if start_date:
                feedbacks = feedbacks.filter(created_at__date__gte=start_date)
        if end_date_str:
            end_date = parse_date(end_date_str)
            if end_date:
                feedbacks = feedbacks.filter(created_at__date__lte=end_date)

        return feedbacks.order_by('-created_at')
    

class ReportExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        institute_id = request.query_params.get('institute_id')
        teacher_id = request.query_params.get('teacher_id')
        subject_id = request.query_params.get('subject_id')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        feedbacks = StudentFeedback.objects.all()
        entity, entity_type = None, None

        if subject_id:
            entity = Subject.objects.filter(id=subject_id).first()
            entity_type = 'subject'
        elif teacher_id:
            entity = User.objects.filter(id=teacher_id, role='teacher').first()
            entity_type = 'teacher'
        elif institute_id:
            entity = Institute.objects.filter(id=institute_id).first()
            entity_type = 'institute'

        feedbacks = filter_feedbacks(feedbacks, start_date_str, end_date_str, entity_type, entity)

        report_data = [
            entity.name if entity_type == 'institute' else '',
            (f"{entity.first_name} {entity.surname}".strip()
             if entity_type == 'teacher' else ''),
            entity.rating if entity_type == 'teacher' else '',
            entity.name if entity_type == 'subject' else '',
            entity.rating if entity_type == 'subject' else '',
            '',
            '',
        ]

        wb = generate_excel_report(feedbacks, report_data)

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
        return response