from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Institute(models.Model):
    name = models.CharField(max_length=255)
    rating = models.FloatField(
        null=True,
        verbose_name='Рейтинг института',
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )