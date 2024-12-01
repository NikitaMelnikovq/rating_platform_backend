from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from accounts.models import User


class Subject(models.Model):
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    rating = models.FloatField(
        null=True,
        verbose_name='Рейтинг предмета',
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )

    def __str__(self):
        return self.name
