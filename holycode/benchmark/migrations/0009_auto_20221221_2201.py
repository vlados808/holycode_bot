# Generated by Django 4.1.4 on 2022-12-21 22:01
import os
import csv


from django.db import migrations


def create_vacancy_types(apps, schema_editor):
    path = f'{os.getcwd()}/benchmark/data/types.csv'
    with open(path) as fp:
        data = list(csv.reader(fp, delimiter=';'))[1:]

    VacancyType = apps.get_model('benchmark', 'VacancyType')
    for line in data:
        vt = VacancyType(
            type=line[0],
            manager=line[1],
            kind=line[2],
            for_recruiter=bool(int(line[3])),
            name=line[4],
        )
        vt.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0008_vacancytype'),
    ]

    operations = [
        migrations.RunPython(create_vacancy_types),
    ]
