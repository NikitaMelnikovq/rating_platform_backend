from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

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

    def __str__(self):
        return f'{self.first_name} {self.surname} {self.last_name}'
    

# Модель формы обратной связи
class Form(models.Model):
    pass 


# Модель института
class Institute(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    rating = models.FloatField(
        verbose_name='Рейтинг института',
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )

# Модель предмета
class Subject(models.Model):
    name = models.CharField(max_length=255)

class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
