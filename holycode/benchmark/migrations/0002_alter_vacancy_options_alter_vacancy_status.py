# Generated by Django 4.1.4 on 2022-12-15 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmark', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vacancy',
            options={'verbose_name_plural': 'Vacancies'},
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='status',
            field=models.CharField(choices=[('открыта', 'Open'), ('закрыта', 'Close'), ('отменена', 'Cancel'), ('не учитывать', 'Ignore'), ('приостановлена', 'Pause')], default='открыта', max_length=50),
        ),
    ]