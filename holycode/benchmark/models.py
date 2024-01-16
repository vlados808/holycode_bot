from django.db import models


class VacancyType(models.Model):

    type = models.CharField(max_length=50, primary_key=True)
    manager = models.CharField(max_length=50, blank=True)
    kind = models.CharField(max_length=50)
    for_recruiter = models.BooleanField(null=True)
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.type


class Vacancy(models.Model):

    class Status(models.TextChoices):
        OPEN = 'открыта'
        CLOSE = 'закрыта'
        CANCEL = 'отменена'
        IGNORE = 'не учитывать'
        PAUSE = 'приостановлена'

    class Currencies(models.TextChoices):
        RUB = 'rubble'
        USD = 'dollar'

    source_id = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=50)
    contact = models.CharField(max_length=50, blank=True)
    vacancy_id = models.CharField(primary_key=True, max_length=50)
    record_id = models.CharField(max_length=50)
    type = models.ForeignKey(VacancyType, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50, choices=Status.choices, blank=True)
    priority = models.IntegerField(blank=True, default=0)
    update = models.DateField(max_length=50)

    name = models.CharField(max_length=50)
    grade = models.CharField(max_length=50)
    experience = models.CharField(max_length=50)
    rate = models.IntegerField(blank=True, default=0)
    rate_currency = models.CharField(max_length=50, choices=Currencies.choices, blank=True)
    quantity = models.IntegerField(blank=True, default=1)

    project_term = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=50, blank=True)
    project = models.CharField(max_length=50, blank=True)
    project_desc = models.CharField(max_length=50, blank=True)
    tasks = models.CharField(max_length=50, blank=True)
    requirements = models.CharField(max_length=50, blank=True)
    additional = models.CharField(max_length=50, blank=True)
    text = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Vacancies'
