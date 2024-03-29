# Generated by Django 4.1.4 on 2022-12-21 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0007_alter_vacancy_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='VacancyType',
            fields=[
                ('type', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('manager', models.CharField(blank=True, max_length=50)),
                ('kind', models.CharField(max_length=50)),
                ('for_recruiter', models.BooleanField(null=True)),
                ('name', models.CharField(blank=True, max_length=50)),
            ],
        ),
    ]
