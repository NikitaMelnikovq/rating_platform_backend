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

class RatingSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        institute_id = request.query_params.get('institute_id')
        teacher_id = request.query_params.get('teacher_id')
        subject_id = request.query_params.get('subject_id')

        # Подготовим базовый набор данных
        # Если ни одного не выбрано, feedbacks пустые не будут использоваться для подсчёта praises
        feedbacks = StudentFeedback.objects.all()

        data = {
            "rating": None,
            "top3": [],
            "bottom3": []
        }

        entity_type = None
        entity = None
        rating = None

        if subject_id:
            entity_type = 'subject'
            try:
                entity = Subject.objects.get(id=subject_id)
                rating = entity.rating
                # Фильтруем отзывы по предмету
                feedbacks = feedbacks.filter(lesson__subject=entity)
            except Subject.DoesNotExist:
                entity = None
        elif teacher_id:
            entity_type = 'teacher'
            try:
                entity = User.objects.get(id=teacher_id, role='teacher')
                rating = entity.rating
                feedbacks = feedbacks.filter(lesson__teacher=entity)
            except User.DoesNotExist:
                entity = None
        elif institute_id:
            entity_type = 'institute'
            try:
                inst = Institute.objects.get(id=institute_id)
                entity = inst
                rating = inst.rating
                feedbacks = feedbacks.filter(lesson__institute=inst)
            except Institute.DoesNotExist:
                entity = None

        data["rating"] = rating

        # Подсчёт топ-3 и bottom-3
        # Логика из предыдущего примера:
        # Если subject_id выбрано -> ищем по урокам (lesson), top3 и bottom3 - пары
        # Если teacher_id -> top3 и bottom3 - пары этого препода
        # Если institute_id -> top3 и bottom3 - преподаватели

        if subject_id and entity:
            # Работаем по предмету: top3 и bottom3 - пары по предмету
            lessons = Lesson.objects.filter(subject=entity).exclude(Q(average_rating__isnull=True) | Q(average_rating=0))
            best_lessons = lessons.order_by('-average_rating')[:3]
            worst_lessons = lessons.order_by('average_rating')[:3]
            data["top3"] = [{"id": l.id, "name": l.topic, "rating": l.average_rating} for l in best_lessons]
            data["bottom3"] = [{"id": l.id, "name": l.topic, "rating": l.average_rating} for l in worst_lessons]

        elif teacher_id and entity:
            # По преподавателю: top3 и bottom3 - пары препода
            lessons = Lesson.objects.filter(teacher=entity).exclude(Q(average_rating__isnull=True) | Q(average_rating=0))
            best_lessons = lessons.order_by('-average_rating')[:3]
            worst_lessons = lessons.order_by('average_rating')[:3]
            data["top3"] = [{"id": l.id, "name": l.topic, "rating": l.average_rating} for l in best_lessons]
            data["bottom3"] = [{"id": l.id, "name": l.topic, "rating": l.average_rating} for l in worst_lessons]

        elif institute_id and entity:
            # По институту: top3 и bottom3 - преподаватели
            teachers = User.objects.filter(institute=entity, role='teacher').exclude(Q(rating__isnull=True) | Q(rating=0))
            best_teachers = teachers.order_by('-rating')[:3]
            worst_teachers = teachers.order_by('rating')[:3]

            def fill_to_three(items):
                arr = [{"id": t.id, "name": f"{t.first_name} {t.surname} {t.last_name or ''}".strip(), "rating": t.rating} for t in items]
                while len(arr) < 3:
                    arr.append(None)
                return arr

            data["top3"] = fill_to_three(best_teachers)
            data["bottom3"] = fill_to_three(worst_teachers)

            # Исключаем повторения
            top_ids = {x["id"] for x in data["top3"] if x}
            for i, item in enumerate(data["bottom3"]):
                if item and item["id"] in top_ids:
                    data["bottom3"][i] = None

        # Если ничего не выбрано или entity = None, data остается с rating=None и пустыми массивами top3, bottom3

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

        entity_type = None
        entity = None
        rating = None
        name_field = ''
        best_worst_praise_available = True

        if subject_id:
            entity_type = 'subject'
            try:
                entity = Subject.objects.get(id=subject_id)
                rating = entity.rating
                name_field = entity.name
                feedbacks = feedbacks.filter(lesson__subject=entity)
            except Subject.DoesNotExist:
                entity = None
        elif teacher_id:
            entity_type = 'teacher'
            try:
                entity = User.objects.get(id=teacher_id, role='teacher')
                rating = entity.rating
                name_field = f"{entity.first_name} {entity.surname} {entity.last_name or ''}".strip()
                feedbacks = feedbacks.filter(lesson__teacher=entity)
            except User.DoesNotExist:
                entity = None
        elif institute_id:
            entity_type = 'institute'
            try:
                inst = Institute.objects.get(id=institute_id)
                entity = inst
                rating = inst.rating
                name_field = inst.name
                feedbacks = feedbacks.filter(lesson__institute=inst)
            except Institute.DoesNotExist:
                entity = None
                best_worst_praise_available = False
        else:
            entity_type = None
            entity = None
            rating = None
            name_field = ''

        # Фильтр по датам
        tz = get_current_timezone()
        if start_date_str:
            start_date = parse_date(start_date_str)
            if start_date:
                start_datetime = make_aware(datetime.combine(start_date, time.min), timezone=tz)
                feedbacks = feedbacks.filter(created_at__gte=start_datetime)
        if end_date_str:
            end_date = parse_date(end_date_str)
            if end_date:
                end_datetime = make_aware(datetime.combine(end_date, time.max), timezone=tz)
                feedbacks = feedbacks.filter(created_at__lte=end_datetime)

        # Подсчет самого частого похвального и критичного mini-отзыва
        good_counts = {}
        bad_counts = {}
        if best_worst_praise_available:
            for fb in feedbacks:
                if not fb.praises:
                    continue
                if fb.rating >= 4:
                    for p in fb.praises:
                        good_counts[p] = good_counts.get(p, 0) + 1
                else:
                    for p in fb.praises:
                        bad_counts[p] = bad_counts.get(p, 0) + 1

        most_frequent_praise = max(good_counts, key=good_counts.get) if good_counts else None
        most_frequent_criticism = max(bad_counts, key=bad_counts.get) if bad_counts else None

        institute_name = ''
        teacher_name = ''
        subject_name = ''
        teacher_rating = None
        subject_rating = None

        if entity_type == 'teacher' and entity:
            teacher_name = name_field
            teacher_rating = rating
            if entity.institute:
                institute_name = entity.institute.name

        elif entity_type == 'subject' and entity:
            subject_name = name_field
            subject_rating = rating
            # Достаём институт и преподавателя через Lesson
            subj_lesson = Lesson.objects.filter(subject=entity).select_related('teacher', 'institute').first()
            if subj_lesson:
                if subj_lesson.institute:
                    institute_name = subj_lesson.institute.name
                if subj_lesson.teacher:
                    teacher_name = f"{subj_lesson.teacher.first_name} {subj_lesson.teacher.surname}".strip()
                    teacher_rating = subj_lesson.teacher.rating

        elif entity_type == 'institute' and entity:
            institute_name = name_field

        # Создаём Excel
        wb = Workbook()
        ws1 = wb.active
        ws1.title = "Основная информация"
        ws1.append([
            "Институт",
            "Преподаватель",
            "Оценка преподавателя",
            "Предмет",
            "Оценка предмета",
            "Лучший отзыв",
            "Худший отзыв"
        ])
        ws1.append([
            institute_name,
            teacher_name,
            teacher_rating if teacher_rating is not None else '',
            subject_name,
            subject_rating if subject_rating is not None else '',
            most_frequent_praise if most_frequent_praise else '',
            most_frequent_criticism if most_frequent_criticism else ''
        ])

        # Вторая страница - отзывы
        ws2 = wb.create_sheet("Отзывы")
        ws2.append(["Студент", "Оценка", "Praises/Не понравилось", "Комментарий", "Преподаватель", "Институт", "Дата и время"])

        feedbacks = feedbacks.select_related('lesson', 'lesson__teacher', 'lesson__institute')

        for fb in feedbacks:
            dt = fb.created_at.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
            result_text = "Понравилось" if fb.rating >=4 else "Не понравилось"
            praises_str = ", ".join(fb.praises) if fb.praises else ''
            teacher_str = ''
            if fb.lesson and fb.lesson.teacher:
                teacher_str = f"{fb.lesson.teacher.first_name} {fb.lesson.teacher.surname}".strip()
            institute_str = fb.lesson.institute.name if fb.lesson.institute else ''

            ws2.append([
                fb.student_name,
                fb.rating,
                praises_str if praises_str else result_text,
                fb.comment or '',
                teacher_str,
                institute_str,
                dt
            ])

        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        filename = "report.xlsx"
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response