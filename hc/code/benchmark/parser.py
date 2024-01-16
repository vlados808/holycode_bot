import re


class TelegramParser:

    @staticmethod
    def remove_emoji(text):
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "]+", flags=re.UNICODE)
        res = emoji_pattern.sub(r'', text)
        return res

    @staticmethod
    def fetch_value(msg, name, reg):
        # match = re.search(reg, msg, re.MULTILINE)
        # value = match.group(name)
        # if value:
        #     value = value.strip()

        values = []
        matches = re.finditer(reg, msg, re.MULTILINE)
        for match in matches:
            try:
                prefix = match.group('prefix')
            except IndexError:
                prefix = None
            value = match.group(name)
            if prefix:
                value = f'{prefix}: {value}'
            value = value.strip()
            value = TelegramParser.remove_emoji(value)
            values.append(value)
        res = '\n'.join(values)

        print(f'VALUE {name}')
        print(res)
        print('')
        return res

    @staticmethod
    def parse_msg(msg):
        regs = {
            'source_number': r'ID: *(?P<source_number>.+)',
            'contact': r'менеджер.*(?P<contact>@.+)',
            'type': r'Вакансия: *(?P<type>.+)\(',
            'grade': r'Вакансия:.*\((?P<grade>.+)\)',
            'experience': r'#Опыт: *(?P<experience>.+)',
            # 'rate': r'#Опыт: *(?P<experience>.+)',
            # 'rate_currency': r'#Опыт: *(?P<experience>.+)',
            # 'quantity': r'#Опыт: *(?P<experience>.+)',
            # 'project_term': r'#Опыт: *(?P<experience>.+)',
            'location': r'(#Регион|#Режим): *(?P<location>.+)',
            'project': r'#Проект: *(?P<project>.+)',
            'project_desc': r'#Проект:.*\n(?P<project_desc>.+)',
            'tasks': r'#Задачи:.*\n(?P<tasks>[\s\S]*?)^\n',
            'requirements': r'#Требования:.*\n(?P<requirements>[\s\S]*?)^\n',
            'additional': r'#(?P<prefix>Старт_работ|Оборудование): *(?P<additional>[\w \.]+)',
        }
        data = {}

        for name, reg in regs.items():
            if value := TelegramParser.fetch_value(msg, name, reg):
                data[name] = value

        return data
