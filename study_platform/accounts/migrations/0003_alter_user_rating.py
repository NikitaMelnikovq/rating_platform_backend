# Generated by Django 5.1.1 on 2024-11-28 16:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_visible_reviews'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='rating',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)], verbose_name='Рейтинг преподавателя'),
        ),
    ]
