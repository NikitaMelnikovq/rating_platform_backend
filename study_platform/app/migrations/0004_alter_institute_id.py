# Generated by Django 5.1.1 on 2024-10-31 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_user_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institute',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
