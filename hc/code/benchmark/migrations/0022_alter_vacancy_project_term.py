# Generated by Django 4.1.4 on 2023-01-17 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0021_alter_vacancy_vacancy_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='project_term',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
