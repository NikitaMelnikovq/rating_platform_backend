# Generated by Django 5.1.1 on 2024-11-28 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0007_lesson_activation_duration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='average_rating',
        ),
    ]
