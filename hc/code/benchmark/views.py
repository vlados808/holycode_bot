import json
import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Vacancy, Source, Resume, ParsingError, GradeConversationError, TypeConversationError, Partner
from .parser import TelegramParser


def check(request):
    print(f'GOT THE REQUEST {request}')
    return HttpResponse("OK")


@csrf_exempt
def process(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f'GOT DATA {data}')
        source_tg = data.get('source')
        text = data.get('msg')
        try:
            source_db = Source.objects.get(pk=source_tg)
        except Source.DoesNotExist as e:
            source_db = Source.create(source_tg)
        print(f'SOURCE DB {source_db}')
        try:
            source_db.parse_tg(text)
        except (ParsingError, GradeConversationError, TypeConversationError) as e:
            # raise e
            print(f'Parsing error {e}')

    return HttpResponse("OK")


@csrf_exempt
def actualize(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f'GOT DATA {data}')
        source_tg = data.get('source')
        if source_tg in ('SkillStaff: новости и запросы на outstaff', 'SmartSourcing'):
            Source.actualize_skillstaff(data)
        elif source_tg in ('SSP SOFT outsourcing', 'SSP SOFT PARTNERS'):
            Source.actualize_ssp(data)

    return HttpResponse("OK")


@csrf_exempt
def close(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f'GOT DATA {data}')
        source_tg = data.get('source')
        if source_tg == 'SmartSourcing':
            Source.close_smartsourcing(data.get('msg'))

    return HttpResponse("OK")


@csrf_exempt
def pause(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f'GOT DATA {data}')
        source_tg = data.get('source')
        if source_tg == 'SmartSourcing':
            Source.close_smartsourcing(data.get('msg'))

    return HttpResponse("OK")


@csrf_exempt
def check_tg_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f'GOT DATA {data}')
        nickname = data.get('nickname')

        user_db = get_object_or_404(Partner, pk=nickname)
        print(f'PARTNER ({user_db})')

    return HttpResponse("OK")


@csrf_exempt
def create_partner(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f'GOT DATA {data}')
        obj = Partner.objects.create(**data)

    return HttpResponse("OK")


@csrf_exempt
def resume(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f'GOT DATA {data}')
        vc_id = data.get('vacancy_id')

        try:
            vc_db = Vacancy.objects.get(pk=vc_id)
        except Vacancy.DoesNotExist as e:
            print(f'no vacancy {vc_id}')
            vc_db = None

        try:
            partner_db = Partner.objects.get(pk=data.get('partner'))
        except Partner.DoesNotExist as e:
            print(f'no partner {data.get("partner")}')
            return HttpResponse("OK")

        additional = '-' if vc_db else f"{settings.CHANNEL_URL}{data.get('vacancy_id')}"
        # print(data.get('resume'))
        data = {
            'vacancy': vc_db,
            'partner': partner_db,
            'name': data.get('name'),
            'city': data.get('city'),
            'grade': data.get('grade'),
            'rate': data.get('rate'),
            # 'resume': data.get('resume').split('holycode')[1],
            'resume': data.get('resume'),
            'date': datetime.datetime.now(),
            'status': 'New',
            'additional': additional,
        }
        obj = Resume.objects.create(**data)

    return HttpResponse("OK")
