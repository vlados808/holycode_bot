# Generated by Django 4.1.4 on 2022-12-21 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0003_vacancy_for_recruiter_vacancy_quantity_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vacancy',
            name='for_recruiter',
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='priority',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
