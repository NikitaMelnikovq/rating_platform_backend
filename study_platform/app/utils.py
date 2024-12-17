from openpyxl import Workbook
from datetime import datetime, time

from django.utils.timezone import get_current_timezone, make_aware
from django.db.models import Q

from accounts.models import User
from lessons.models import StudentFeedback, Lesson
from subjects.models import Subject
from institute.models import Institute

def filter_feedbacks(feedbacks, start_date_str, end_date_str, entity_type, entity):
    tz = get_current_timezone()
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        start_datetime = make_aware(datetime.combine(start_date, time.min), timezone=tz)
        feedbacks = feedbacks.filter(created_at__gte=start_datetime)

    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        end_datetime = make_aware(datetime.combine(end_date, time.max), timezone=tz)
        feedbacks = feedbacks.filter(created_at__lte=end_datetime)

    if entity_type == 'subject':
        feedbacks = feedbacks.filter(lesson__subject=entity)
    elif entity_type == 'teacher':
        feedbacks = feedbacks.filter(lesson__teacher=entity)
    elif entity_type == 'institute':
        feedbacks = feedbacks.filter(lesson__institute=entity)
    return feedbacks


def generate_excel_report(feedbacks, report_data):
    wb = Workbook()

    ws1 = wb.active
    ws1.title = 'Основная информация'
    ws1.append([
        'Институт', 'Преподаватель', 'Оценка преподавателя',
        'Предмет', 'Оценка предмета', 'Лучший отзыв', 'Худший отзыв'
    ])
    ws1.append(report_data)

    ws2 = wb.create_sheet('Отзывы')
    ws2.append([
        'Студент', 'Оценка', 'Praises/Не понравилось',
        'Комментарий', 'Преподаватель', 'Институт', 'Дата и время'
    ])

    for fb in feedbacks:
        ws2.append([
            fb.student_name,
            fb.rating,
            ', '.join(fb.praises) if fb.praises else '',
            fb.comment or '',
            (f"{fb.lesson.teacher.first_name} {fb.lesson.teacher.surname}".strip()
             if fb.lesson and fb.lesson.teacher else ''),
            fb.lesson.institute.name if fb.lesson.institute else '',
            fb.created_at.astimezone(get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')
        ])

    return wb

def get_entity_and_feedbacks(institute_id, teacher_id, subject_id):
    feedbacks = StudentFeedback.objects.all()
    entity, entity_type, rating = None, None, None

    if subject_id:
        entity_type = 'subject'
        entity = Subject.objects.filter(id=subject_id).first()
        if entity:
            rating = entity.rating
            feedbacks = feedbacks.filter(lesson__subject=entity)
    elif teacher_id:
        entity_type = 'teacher'
        entity = User.objects.filter(id=teacher_id, role='teacher').first()
        if entity:
            rating = entity.rating
            feedbacks = feedbacks.filter(lesson__teacher=entity)
    elif institute_id:
        entity_type = 'institute'
        entity = Institute.objects.filter(id=institute_id).first()
        if entity:
            rating = entity.rating
            feedbacks = feedbacks.filter(lesson__institute=entity)

    return entity, entity_type, rating, feedbacks


def get_lesson_ratings(entity, filter_by):
    lessons = Lesson.objects.filter(**filter_by).exclude(
        Q(average_rating__isnull=True) | Q(average_rating=0)
    )
    best_lessons = lessons.order_by('-average_rating')[:3]
    worst_lessons = lessons.order_by('average_rating')[:3]

    return [
        {'id': l.id, 'name': l.topic, 'rating': l.average_rating}
        for l in best_lessons
    ], [
        {'id': l.id, 'name': l.topic, 'rating': l.average_rating}
        for l in worst_lessons
    ]


def get_teacher_ratings(entity):
    teachers = User.objects.filter(
        institute=entity, role='teacher'
    ).exclude(Q(rating__isnull=True) | Q(rating=0))

    best_teachers = teachers.order_by('-rating')[:3]
    worst_teachers = teachers.order_by('rating')[:3]

    def fill_to_three(items):
        arr = [
            {
                'id': t.id,
                'name': f'{t.first_name} {t.surname} {t.last_name or ""}'.strip(),
                'rating': t.rating,
            }
            for t in items
        ]
        while len(arr) < 3:
            arr.append(None)
        return arr

    top3 = fill_to_three(best_teachers)
    bottom3 = fill_to_three(worst_teachers)

    top_ids = {x['id'] for x in top3 if x}
    for i, item in enumerate(bottom3):
        if item and item['id'] in top_ids:
            bottom3[i] = None

    return top3, bottom3