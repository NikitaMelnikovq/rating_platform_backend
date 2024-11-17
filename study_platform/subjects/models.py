from django.db import models

from accounts.models import User
# Create your models here.
class Subject(models.Model):
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name
    
    