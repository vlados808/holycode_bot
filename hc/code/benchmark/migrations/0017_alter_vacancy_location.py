# Generated by Django 4.1.4 on 2023-01-09 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0016_alter_source_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='location',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]