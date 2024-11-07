import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Модель пользователя
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="admin")
    surname = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    institute = models.ForeignKey('Institute', on_delete=models.CASCADE)
    rating = models.FloatField(
        null=True,
        verbose_name='Рейтинг преподавателя',
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )

    def __str__(self):
        return f'{self.first_name} {self.surname} {self.last_name}'
    

# Модель формы обратной связи
class Form(models.Model):
    pass 


# Модель института
class Institute(models.Model):
    name = models.CharField(max_length=255)
    rating = models.FloatField(
        verbose_name='Рейтинг института',
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )

# Модель предмета
class Subject(models.Model):
    name = models.CharField(max_length=255)
    teacher_id = models.ForeignKey("User", on_delete=models.CASCADE, default=0)

class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class FormLink(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        return self.is_active and timezone.now() < self.expires_at