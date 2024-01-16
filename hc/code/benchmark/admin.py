from datetime import datetime, timedelta

import requests

from django.contrib import admin, messages
from django.db import models
from .models import Vacancy, VacancyType, Source, Publication, VacancyStatus, Resume, Partner, Digest
from django_admin_listfilter_dropdown.filters import DropdownFilter
from django_json_widget.widgets import JSONEditorWidget
from django.forms import TextInput, Textarea
from django.forms.models import model_to_dict
from django.template.defaultfilters import truncatechars
from django.conf import settings


@admin.action(description='Publish in the internal channel')
def send(modeladmin, request, queryset):
    for vacancy in queryset:
        vacancy.send('new')
        messages.info(request, f"Vacancy {vacancy} sent")


@admin.action(description='Publish in the partner channel')
def send_btn(modeladmin, request, queryset):
    for vacancy in queryset:
        vacancy.send('btn')
        messages.info(request, f"Vacancy {vacancy} sent")


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):

    # fieldsets = (
    #     (None, {
    #         'fields': (
    #             'source_number',
    #             'source',
    #             'contact',
    #             'vacancy_id',
    #             'type',
    #             'status',
    #             'priority',
    #             'update',
    #         )
    #     }),
    #     (None, {
    #         'fields': (
    #             'name',
    #             'grade',
    #             'experience',
    #             'rate',
    #             'rate_currency',
    #             'quantity',
    #         )
    #     }),
    #     (None, {
    #         'fields': (
    #             'project_term',
    #             'location',
    #             'project',
    #             'project_desc',
    #             'tasks',
    #             'requirements',
    #             'additional',
    #             'text',
    #         )
    #     }),
    # )

    list_display = (
        'name',
        'vacancy_kind',
        'short_source',
        'short_id',
        'rate',
        'status',
        'short_project',
        'last_publication',
        'update',
    )
    actions = [send, send_btn]
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
        'last_publication',
    )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '100'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 100})},
    }

    @admin.display(description='kind', ordering='type__kind')
    def vacancy_kind(self, obj):
        if obj.type:
            return obj.type.kind
        return None

    @admin.display(description='project', ordering='project')
    def short_project(self, obj):
        if obj.project:
            return truncatechars(obj.project, 20)
        return truncatechars(obj.project_desc, 20)

    @admin.display(description='source', ordering='source')
    def short_source(self, obj):
        return truncatechars(obj.source, 20)

    def save_model(self, request, obj, form, change):
        print(obj.project)
        prev_id = obj.vacancy_id
        new_id = obj.vacancy_id

        status_changed = False
        prev_status = VacancyStatus.objects.filter(vacancy=obj).order_by('-date').first()
        if not prev_status or prev_status.status != obj.status:
            status_changed = True

        if new_id != prev_id:
            print(f'{prev_id} -> {new_id}')
            obj.vacancy_id = new_id
            vc = Vacancy.objects.filter(pk=prev_id).first()
            vc.delete()

        super().save_model(request, obj, form, change)

        if status_changed:
            now = datetime.now()
            data = {
                'vacancy': obj,
                'status': obj.status,
                'date': now
            }
            VacancyStatus.objects.create(**data)


@admin.register(VacancyType)
class VacancyTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'manager', 'kind', 'for_recruiter', 'name')


@admin.action(description='Parse selected sources')
def parse(modeladmin, request, queryset):
    for source in queryset:
        if source.type == 'telegram':
            messages.error(request, f"Parsing is not allowed for tg sources ({source.name})")
            continue
        elif source.type in ('google sheet', 'xml'):
            if not source.url:
                messages.error(request, f"Empty url in source ({source.name})")
                continue
            # source.parse()
            source.actualize()
            messages.info(request, f"Successfully parsed ({source.name})")
        elif source.type == 'file':
            if not source.file:
                messages.error(request, f"Empty file in source ({source.name})")
                continue
            source.actualize()
            # source.parse()
            messages.info(request, f"Successfully parsed ({source.name})")


@admin.action(description='Make digest')
def digest(modeladmin, request, queryset):
    now = datetime.now()
    prev_digest = Digest.objects.order_by('-date').first()
    prev_date = prev_digest.date if prev_digest else now - timedelta(days=8)
    changes = VacancyStatus.objects.filter(
        status__in=['приостановлена', 'закрыта'],
        date__gte=prev_date
    )

    # partner_pubs = [x.vacancy for x in Publication.objects.filter(partner_publication=True).distinct('vacancy')]
    partner_pubs = {x.vacancy: x.message_id for x in Publication.objects.filter(partner_publication=True).distinct('vacancy')}
    # print(model_to_dict(changes[0]))
    # print(partner_pubs)
    # return

    res = {}
    res_partner_stop = {}
    seen_vc = set()

    for element in changes:
        if element.vacancy.short_id in seen_vc:
            continue
        seen_vc.add(element.vacancy.short_id)
        if not res.get(element.vacancy.source.name):
            res[element.vacancy.source.name] = {}
        source = res[element.vacancy.source.name]
        if not source.get(element.status):
            source[element.status] = []
        source[element.status].append({
            'short_id': element.vacancy.short_id,
            'name': element.vacancy.name,
            'manager': element.vacancy.type.manager,
        })

        if element.vacancy in partner_pubs:
            if not res_partner_stop.get(element.status):
                res_partner_stop[element.status] = []
            res_partner_stop[element.status].append({
                'short_id': element.vacancy.short_id,
                'name': element.vacancy.name,
                'manager': element.vacancy.type.manager,
                'msg_id': partner_pubs.get(element.vacancy),
            })

    res_partner_open = {}
    for element, msg_id in partner_pubs.items():
        if element.status != 'открыта':
            continue
        if not res_partner_open.get(element.type.kind):
            res_partner_open[element.type.kind] = {}
        kind = res_partner_open[element.type.kind]
        if not kind.get(element.type.type):
            kind[element.type.type] = []
        kind[element.type.type].append({
            'short_id': element.short_id,
            'name': element.name,
            'manager': element.type.manager,
            'msg_id': msg_id,
        })

    if res:
        url = f'{settings.BOT_URL}digest'
        response = requests.post(url, json=res)

        if response.status_code == 200:
            data = {'date': now}
            if prev_digest:
                prev_digest.date = now
                prev_digest.save()
            else:
                Digest.objects.create(**data)

    if res_partner_stop:
        url = f'{settings.BOT_URL}digest_partner_stop'
        response = requests.post(url, json=res_partner_stop)

    if res_partner_open and now.weekday() in (0, 2, 4):
        url = f'{settings.BOT_URL}digest_partner_open'
        response = requests.post(url, json=res_partner_open)


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    actions = [parse, digest]
    list_display = ('name', 'type')
    list_filter = ('type', )
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
        models.CharField: {'widget': TextInput(attrs={'size': '100'})},
    }


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'chat_id', 'last_published')


@admin.register(VacancyStatus)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'status', 'date')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'vacancy_name',
        'short_id',
        'vacancy_source',
        'status',
        'manager',
        'city',
        'grade',
        'rate',
        'partner_brand',
        'date',
        'file_link',
    )
    list_filter = (
        'vacancy__source',
        'status',
        'partner__company_name',
        'city',
        'grade',
        'date',
    )

    @admin.display(description='source_number', ordering='vacancy__source_number')
    def source_number(self, obj):
        if obj.vacancy:
            return obj.vacancy.source_number
        return None

    @admin.display(description='short_id', ordering='vacancy__short_id')
    def short_id(self, obj):
        if obj.vacancy:
            return obj.vacancy.short_id
        return None

    @admin.display(description='vacancy_name', ordering='vacancy__name')
    def vacancy_name(self, obj):
        if obj.vacancy:
            return obj.vacancy.name
        return None

    @admin.display(description='vacancy_source', ordering='vacancy__source')
    def vacancy_source(self, obj):
        if obj.vacancy:
            return obj.vacancy.source
        return None

    @admin.display(description='partner_name', ordering='partner__name')
    def partner_name(self, obj):
        if obj.partner:
            return obj.partner.name
        return None

    @admin.display(description='partner_brand', ordering='partner__brand_name')
    def partner_brand(self, obj):
        if obj.partner:
            return obj.partner.brand_name
        return None

    @admin.display(description='manager', ordering='vacancy__type__manager')
    def manager(self, obj):
        if obj.vacancy:
            return obj.vacancy.type.manager
        return None


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'name', 'company_name', 'brand_name')


# @admin.register(Digest)
# class DigestAdmin(admin.ModelAdmin):
#     list_display = ('date', )
