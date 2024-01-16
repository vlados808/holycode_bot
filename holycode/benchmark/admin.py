from django.contrib import admin
from .models import Vacancy, VacancyType
from django_admin_listfilter_dropdown.filters import DropdownFilter


def get_kind(vacancy):
    return vacancy.type.kind


def get_manager(vacancy):
    return vacancy.type.manager


def get_for_recruiter(vacancy):
    return vacancy.type.for_recruiter


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': (
                'source_id',
                'source',
                'contact',
                'vacancy_id',
                'record_id',
                'type',
                # get_kind,
                # get_manager,
                'status',
                'priority',
                'update',
                # get_for_recruiter,
            )
        }),
        (None, {
            'fields': (
                'name',
                'grade',
                'experience',
                'rate',
                'rate_currency',
                'quantity',
            )
        }),
        (None, {
            'fields': (
                'project_term',
                'location',
                'project',
                'project_desc',
                'tasks',
                'requirements',
                'additional',
                'text',
            )
        }),
    )
    list_display = ('name', 'source', 'project_term', 'rate', 'update', 'status')
    list_filter = (
        'source',
        ('type', DropdownFilter),
        ('type__kind', DropdownFilter),
        ('type__manager', DropdownFilter),
        'status',
        'priority',
        'update',
        'type__for_recruiter',
        'rate',
    )


@admin.register(VacancyType)
class VacancyTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'manager', 'kind', 'for_recruiter', 'name')
