from celery import shared_task
from .models import StudentFeedback, Lesson
from django.db import models 


@shared_task
def calculate_lesson_rating(lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    feedbacks = StudentFeedback.objects.filter(lesson=lesson)
    total_feedbacks = feedbacks.count()
    if total_feedbacks > 0:
        average_rating = feedbacks.aggregate(models.Avg('rating'))['rating__avg']
        lesson.average_rating = average_rating
        lesson.feedback_count = total_feedbacks
        lesson.save(update_fields=['average_rating', 'feedback_count'])


@shared_task
def process_feedback(feedback_data):
    lesson_id = feedback_data.pop('lesson')

    lesson = Lesson.objects.get(id=lesson_id)
    if not lesson.is_link_active():
        return

    feedback = StudentFeedback.objects.create(lesson=lesson, **feedback_data)

    calculate_lesson_rating.delay(lesson.id)