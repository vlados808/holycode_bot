# Generated by Django 4.1.4 on 2023-01-31 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0029_alter_publication_last_published_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='short_id',
            field=models.CharField(max_length=8, null=True),
        ),
    ]
