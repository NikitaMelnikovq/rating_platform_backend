from celery import shared_task
from django.db.models import Avg, Q

from .models import StudentFeedback, Lesson
from accounts.models import User
from institute.models import Institute
from subjects.models import Subject


@shared_task
def process_feedback(feedback_data):
    lesson_id = feedback_data.pop('lesson')

    lesson = Lesson.objects.get(id=lesson_id)
    if not lesson.is_link_active():
        return

    StudentFeedback.objects.create(lesson=lesson, **feedback_data)


@shared_task
def update_lesson_rating(lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    feedbacks = StudentFeedback.objects.filter(lesson=lesson).exclude(
        Q(rating__isnull=True) | Q(rating=0)
    )

    if feedbacks.exists(): 
        lesson.average_rating = feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0
        lesson.feedback_count = feedbacks.count()
    else:
        lesson.average_rating = None
        lesson.feedback_count = 0

    lesson.save()

    update_subject_rating.delay(lesson.subject_id)
    update_teacher_rating.delay(lesson.teacher_id)
    update_institute_rating.delay(lesson.institute_id)


@shared_task
def update_subject_rating(subject_id):
    subject = Subject.objects.get(id=subject_id)
    lessons = Lesson.objects.filter(subject=subject).exclude(
        Q(average_rating__isnull=True) | Q(average_rating=0)
    )
    subject_avg_rating = lessons.aggregate(
        Avg('average_rating'))['average_rating__avg'] or 0
    subject.rating = subject_avg_rating

    subject.save()


@shared_task
def update_teacher_rating(teacher_id):
    teacher = User.objects.get(id=teacher_id, role='teacher')
    subjects = Subject.objects.filter(teacher=teacher).exclude(Q(rating__isnull=True) | Q(rating=0))
    teacher_avg_rating = subjects.aggregate(Avg('rating'))['rating__avg'] or 0
    teacher.rating = teacher_avg_rating

    teacher.save()


@shared_task
def update_institute_rating(institute_id):
    institute = Institute.objects.get(id=institute_id)
    teachers = User.objects.filter(institute=institute, role='teacher')
    teachers_with_valid_ratings = teachers.exclude(
        Q(rating__isnull=True) | Q(rating=0)
    )
    institute_avg_rating = teachers_with_valid_ratings.aggregate(
        Avg('rating'))['rating__avg'] or 0
    institute.rating = institute_avg_rating

    institute.save()


@shared_task
def recalculate_all_ratings():
    lessons = Lesson.objects.all()

    for lesson in lessons:
        update_lesson_rating.delay(lesson.id)