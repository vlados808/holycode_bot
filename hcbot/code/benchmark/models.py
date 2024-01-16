import re
import pprint
import datetime
from urllib.parse import urlparse
from hashlib import md5

from django.db import models
from django.forms.models import model_to_dict


class ParsingError(BaseException):
    pass


class TypeConversationError(BaseException):
    pass


class GradeConversationError(BaseException):
    pass


class VacancyType(models.Model):

    type = models.CharField(max_length=50, primary_key=True)
    manager = models.CharField(max_length=50, blank=True)
    kind = models.CharField(max_length=50)
    for_recruiter = models.BooleanField(null=True)
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.type


class Source(models.Model):

    class SourceType(models.TextChoices):
        TG = 'telegram'
        GS = 'google sheet'
        XL = 'file'

    name = models.CharField(max_length=50, primary_key=True)
    type = models.CharField(max_length=50, choices=SourceType.choices, blank=True)
    url = models.CharField(max_length=500, blank=True)
    instruction = models.JSONField()
    file = models.FileField(upload_to='vacancy_file', blank=True)

    def parse_tg(self, msg):
        print('PROCESS')
        print(msg)
        instruction = self.instruction
        sub_res = {
            'source': self,
            'update': datetime.date.today(),
            'text': msg,
        }
        # value = msg.lower()

        for param in instruction:
            value = msg

            if param.get('value') and param.get('name'):
                sub_res[param.get('name')] = param.get('value')
                continue

            if reg := param.get('reg'):

                matches = re.finditer(reg, value, re.MULTILINE)
                values = [x.group() for x in matches]
                if values:
                    value = values[0]
                else:
                    value = ''
                # value = '\n'.join([x.group() for x in matches])

            if param.get('required'):
                if not value:
                    raise ParsingError

            if param_type := param.get('type'):
                if value:
                    if param_type == 'int':
                        value = int(value)

            value = value.lower()

            if name := param.get('name'):
                if value:
                    if sub_res.get(name):
                        sub_res[name] += value
                    else:
                        sub_res[name] = value

            # print(f'PARAM {param}')
            # print(f'VALUE {value}')


        Vacancy.create(sub_res)

    def process_xls_line(self, raw_line):
        instruction = self.instruction
        sub_res = {
            'source': self,
            'update': datetime.date.today(),
            'text': [],
        }

        for param in instruction:

            if param.get('value') and param.get('name'):
                sub_res[param.get('name')] = param.get('value')
                continue

            line = raw_line
            value = line[param.get('column')].value
            if value is None:
                continue
            sub_res['text'].append(value)
            value = value.lower()

            if reg := param.get('reg'):
                reg = re.compile(reg)
                value = reg.findall(value)
                if value:
                    value = value[0]
                else:
                    value = ''

            if param.get('required'):
                if not value:
                    raise ParsingError

            if param_type := param.get('type'):
                if value:
                    if param_type == 'int':
                        value = int(value)

            if name := param.get('name'):
                if value:
                    if sub_res.get(name):
                        sub_res[name] = ' '.join([sub_res[name], value])
                    else:
                        sub_res[name] = value

        sub_res['text'] = '\n'.join(sub_res['text'])
        Vacancy.create(sub_res)

    def process_line(self, raw_line, raw_data):
        print('PROCESS')
        print(raw_line)
        instruction = self.instruction
        sub_res = {
            'source': self,
            'update': datetime.date.today(),
            'text': '\n'.join(raw_line),
        }

        for param in instruction:

            if param.get('value') and param.get('name'):
                sub_res[param.get('name')] = param.get('value')
                continue

            if param.get('line') != 'inline':
                line = raw_data[param.get('line')]
            else:
                line = raw_line

            value = line[param.get('column')]
            value = value.lower()

            if reg := param.get('reg'):
                reg = re.compile(reg)
                value = reg.findall(value)
                if value:
                    value = value[0]
                else:
                    value = ''

            if param.get('required'):
                if not value:
                    raise ParsingError

            if param_type := param.get('type'):
                if value:
                    if param_type == 'int':
                        value = int(value)

            if name := param.get('name'):
                if value:
                    if sub_res.get(name):
                        sub_res[name] += value
                    else:
                        sub_res[name] = value

        Vacancy.create(sub_res)

    def __str__(self):
        return self.name


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

    source_number = models.CharField(max_length=50, blank=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True)
    contact = models.CharField(max_length=50, blank=True)
    vacancy_id = models.CharField(max_length=32, primary_key=True)
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
    location = models.CharField(max_length=500, blank=True)
    project = models.CharField(max_length=100, blank=True)
    project_desc = models.TextField(blank=True)
    tasks = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    additional = models.TextField(blank=True)
    text = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Vacancies'

    @classmethod
    def create(cls, data):
        print('PRERES')
        pprint.pprint(data)

        try:
            cls.convert_type(data)
            cls.convert_grade(data)
            cls.check_experience(data)
            cls.create_name(data)
            cls.create_id(data)
        except Exception as e:
            print(f'catch exception in create {e}')
            return

        try:
            vacancy_db = cls.objects.get(pk=data['vacancy_id'])
        except cls.DoesNotExist:
            cls.objects.create(**data)
            print(f"vacancy {data['vacancy_id']} created")
            return

        to_update = cls.find_changes(vacancy_db, data)
        if to_update:
            cls.objects.filter(pk=data['vacancy_id']).update(**to_update)
            print(f"vacancy {data['vacancy_id']} updated with {to_update}")
            return

        print(f"vacancy {data['vacancy_id']} is already exist")

    @staticmethod
    def convert_type(data):
        type_map = {
            "JavaScript": "JS",
            "js": "JS",
            "javascript": "JS",
            "java script": "JS",
            "Тестировщик ручной": "Manual QA",
            "тестирование ручное": "Manual QA",
            "Системный аналитик": "System Analyst",
            "системный аналитик": "System Analyst",
            "systemanalyst": "System Analyst",
            "python": "Python",
            "c++": "C++",
            "c#": ".NET",
            "frontend": "FrontEnd",
            "front end": "FrontEnd",
            "full-stack": "FullStack",
            "fullstack": "FullStack",
            "ios": "iOS",
            "разработчик ios": "iOS",
            "android": "Android",
            "разработчик android": "Android",
            "devops": "DevOps",
            "ror разработчик": "Ruby",
            "java разработчик": "Java",
            "разработчик java": "Java",
            "qa manual": "Manual QA",
            "qa": "Manual QA",
            "devops/sre": "DevOps",
            "ручной тестировщик": "Manual QA",
            "react": "React",
            "разработчик react": "React",
            "angular": "Angular",
        }
        type_str = type_map.get(data.get('type'))
        if not type_str:
            raise TypeConversationError(f"Can't find type in mapping {data.get('type')}")
        try:
            type_db = VacancyType.objects.get(pk=type_str)
        except VacancyType.DoesNotExist:
            raise TypeConversationError(f"Can't find type in db {type_str}")
        data['type'] = type_db

    @staticmethod
    def convert_grade(data):
        grade_map = {
            'джун': 'Junior',
            'джуниор': 'Junior',
            'junior': 'Junior',
            'мид': 'Middle',
            'мидл': 'Middle',
            'миддл': 'Middle',
            'middle': 'Middle',
            'мид+': 'Middle+',
            'мид +': 'Middle+',
            'мидл+': 'Middle+',
            'мидл +': 'Middle+',
            'миддл+': 'Middle+',
            'миддл +': 'Middle+',
            'middle+': 'Middle+',
            'middle +': 'Middle+',
            'сениор': 'Senior',
            'сеньор': 'Senior',
            'сеньер': 'Senior',
            'сеньёр': 'Senior',
            'синиор': 'Senior',
            'синьор': 'Senior',
            'синьер': 'Senior',
            'синьёр': 'Senior',
            'senior': 'Senior',
            'архитектор': 'Architect',
            'architect': 'Architect',
        }
        grade_str = grade_map.get(data.get('grade'))
        if not grade_str:
            raise GradeConversationError(f"Can't find grade in mapping {data.get('grade')}")
        data['grade'] = grade_str

    @staticmethod
    def check_experience(data):
        exp_mapping = {
            'Junior': 'от 1 года',
            'Middle': 'от 2 лет',
            'Middle+': 'от 3 лет',
            'Senior': 'от 4 лет',
            'Architect': 'от 6 лет',
        }
        if data.get('experience'):
            return
        data['experience'] = exp_mapping.get(data.get('grade'), '')

    @staticmethod
    def create_name(data):
        name_parts = (x for x in (data.get('grade'), data['type'].type, data['type'].name) if x)
        data['name'] = ' '.join(name_parts)

    @staticmethod
    def create_id(data):
        val = ''.join([data.get('name', ''), data.get('project', ''), data.get('project_desc', '')])
        val = val.encode('utf-8')
        val = md5(val)
        val = val.hexdigest()
        data['vacancy_id'] = val

    @staticmethod
    def find_changes(vacancy, data):
        vacancy_dict = model_to_dict(vacancy)
        for attr in ('name', 'project', 'project_desc', 'vacancy_id', 'update', 'priority', 'status', 'type', 'source'):
            vacancy_dict.pop(attr)
        res = {}
        for key, value in vacancy_dict.items():
            if data.get(key, '') != value:
                if value == 0 and data.get(key) is None:
                    continue
                if key == 'quantity' and data.get(key) is None:
                    continue
                print(f"FIND CHANGES {key} {value} -> {data.get(key)}")
                res[key] = data.get(key)
        if res:
            res['update'] = data.get('update')
        return res
