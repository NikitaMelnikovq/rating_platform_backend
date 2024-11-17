from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

from institute.models import Institute

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="admin")
    surname = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    rating = models.FloatField(
        null=True,
        verbose_name='Рейтинг преподавателя',
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )

    def __str__(self):
        return f'{self.first_name} {self.surname} {self.last_name}'