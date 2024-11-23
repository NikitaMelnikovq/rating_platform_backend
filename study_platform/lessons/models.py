import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

from accounts.models import User
from institute.models import Institute
from subjects.models import Subject

class Lesson(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    unique_code = models.UUIDField(default=uuid.uuid4, unique=True)
    is_active = models.BooleanField(default=True)
    activation_duration = models.DurationField(default=timedelta(minutes=10))
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    qr_code_base64 = models.TextField(null=True, blank=True)
    average_rating = models.FloatField(default=0.0)
    feedback_count = models.PositiveIntegerField(default=0)

    def get_unique_link(self):
        return f'/lesson/{self.unique_code}/'

    def is_link_active(self):
        if not self.is_active:
            return False
        return timezone.now() <= self.end_time

    def __str__(self):
        return f'Lesson: {self.topic} by {self.teacher}'
    

class FormLink(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        return self.is_active and timezone.now() < self.expires_at
    

class StudentFeedback(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    praises = models.JSONField(default=list)  # To store selected praises
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback by {self.student_name} for {self.lesson}'