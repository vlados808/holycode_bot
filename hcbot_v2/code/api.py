import asyncio
import json
import os
from pprint import pprint
import re
from datetime import date, datetime

from aiohttp import web, ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ContentType, KeyboardButton, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove
import aiogram.utils.markdown as md
from aiogram.utils.exceptions import RetryAfter, MessageIsTooLong
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

BOT_IS_RUNNING = False
# BOT_TOKEN = "620850149:AAHmY3G1xlF2LFWBgCjTdfRQEiM4mz_Dx-o"  # prod
# BOT_TOKEN = "5932142609:AAEFir6ntqtHe0ZVy_rmKs6TpoEKRUvRQRE"  dev
# BOT_TOKEN = "5679648270:AAECB0EzPQ8YkCtVOx1e7W8Dw89TgCetQ6Q"  new prod
# BOT_TOKEN = "https://t.me/Outstaff_requests_bot"  new prod
# BOT_TOKEN = "https://t.me/Outstaff_requests_bot"  new prod https://t.me/c/1875910106/100
BOT_TOKEN = os.getenv('BOT_TOKEN', "5932142609:AAEFir6ntqtHe0ZVy_rmKs6TpoEKRUvRQRE")
# https://t.me/tt17me_bot - prod https://t.me/nn17me_bot - dev https://t.me/Outstaff_requests_bot - new prod
# https://t.me/c/1875910106/215 - example to the partnermsg url
BOT_URL = os.getenv('BOT_URL', 'https://t.me/nn17me_bot')
# CHAT_ID = -1001879463885 prod
# CHAT_ID = 242190616 dev
CHAT_ID = int(os.getenv('CHAT_ID', "242190616"))
CHAT_PARTNERS_ID = int(os.getenv('CHAT_PARTNERS_ID', "242190616"))
# PROC_URL = 'http://web:8000/process/' prod
# PROC_URL = 'http://127.0.0.1:8000/process/' dev
PROC_URL = os.getenv('PROC_URL', "http://127.0.0.1:8000/")


bot = Bot(token=BOT_TOKEN)


async def user_is_registered(event: types.Message):

    data = {
        'nickname': event.from_user.username,
    }

    url = f'{PROC_URL}check_tg_user/'
    async with ClientSession() as session:
        res = await session.post(url, json=data)
    return res.status == 200


def check_start(func):
    async def wrapper(*args, **kwargs):
        if args[0].text and args[0].text.startswith('/start'):
            return await handle_start(*args, **kwargs)
        return await func(*args, **kwargs)

    return wrapper


class Form(StatesGroup):
    vacancy = State()
    name = State()
    city = State()
    grade = State()
    rate = State()
    resume = State()


class RegistrationForm(StatesGroup):
    name = State()
    company_name = State()
    brand_name = State()
    country = State()
    other_countries = State()
    inn = State()
    contact = State()
    email = State()


async def handle_start(event: types.Message, state: FSMContext, **kwargs):

    if await user_is_registered(event):
        await handle_vacancy_flow(event, state)
    else:
        await handle_registration_flow(event, state)


# @check_start
async def handle_registration_flow(event: types.Message, state: FSMContext):
    await event.reply('''
        Мы рады приветствовать новых партнеров нашего сервиса.
Для продуктивной работы и возможности откликаться на наши вакансии необходимо пройти регистрацию и ответить на несколько наших вопросов
    ''')
    await RegistrationForm.name.set()
    await event.reply('Укажите ваши Фамилию и Имя')


@check_start
async def registration_name(event: types.Message, state: FSMContext, **kwargs):

    async with state.proxy() as data:
        data['name'] = event.text

    await RegistrationForm.next()
    await event.reply("Укажите юридическое название компании")
    # print(state.)


@check_start
async def registration_company_name(event: types.Message, state: FSMContext, **kwargs):

    async with state.proxy() as data:
        data['company_name'] = event.text

    await RegistrationForm.next()
    await event.reply("Укажите название бренда вашей компании")


@check_start
async def registration_brand_name(event: types.Message, state: FSMContext, **kwargs):

    async with state.proxy() as data:
        data['brand_name'] = event.text

    await RegistrationForm.next()
    await event.reply("Укажите страну регистрации ЮЛ")


@check_start
async def registration_country(event: types.Message, state: FSMContext, **kwargs):

    async with state.proxy() as data:
        data['country'] = event.text

    await RegistrationForm.next()
    await event.reply("Если у вас есть ЮЛ в других странах, перечислите их, иначе напишите НЕТ")


@check_start
async def registration_other_countries(event: types.Message, state: FSMContext, **kwargs):

    async with state.proxy() as data:
        data['other_countries'] = event.text

    await RegistrationForm.next()
    await event.reply("Укажите ИНН вашего ЮЛ")


@check_start
async def registration_inn(event: types.Message, state: FSMContext, **kwargs):

    reg = re.compile('^\\d+$')
    if not re.match(reg, event.text):
        await event.reply("Введите корректный ИНН")
        return

    async with state.proxy() as data:
        data['inn'] = event.text

    await RegistrationForm.next()
    await event.reply("Укажите контактный телефон")


@check_start
async def registration_contact(event: types.Message, state: FSMContext, **kwargs):

    reg = re.compile('^\\+?[\\d \\(\\)\\-]+$')
    if not re.match(reg, event.text):
        await event.reply("Введите корректный номер телефона")
        return

    async with state.proxy() as data:
        data['contact'] = event.text

    await RegistrationForm.next()
    await event.reply("Укажите контактный email")


@check_start
async def registration_email(event: types.Message, state: FSMContext, **kwargs):

    reg = re.compile('^[a-zA-Z0-9]+[\\._]?[ a-zA-Z0-9]+[@][\\w\\-]+[. ]\\w{2,3}$')
    if not re.match(reg, event.text):
        await event.reply("Введите корректный email")
        return

    async with state.proxy() as data:
        data['email'] = event.text

    post_data = {'nickname': event.from_user.username}

    async with state.proxy() as data:
        post_data['name'] = data['name']
        post_data['company_name'] = data['company_name']
        post_data['brand_name'] = data['brand_name']
        post_data['registration_country'] = data['country']
        post_data['other_countries'] = data['other_countries']
        post_data['inn'] = data['inn']
        post_data['phone'] = data['contact']
        post_data['email'] = data['email']

    url = f'{PROC_URL}create_partner/'
    async with ClientSession() as session:
        await session.post(url, json=post_data)

    await event.reply("Спасибо! Вы зарегистрированы в нашей партнерской сети. Для продолжения работы и отклика на вакансию вам необходимо снова откликнуться в канале")
    await state.finish()


async def handle_vacancy_flow(event: types.Message, state: FSMContext, **kwargs):
    print(event.text)
    # try:
    _, vacancy_id = event.text.split()
    # except ValueError:
    #     await event.reply("Необходимо заново откликнуться на вакансию")
    #     return

    await Form.vacancy.set()
    async with state.proxy() as data:
        data['vacancy'] = vacancy_id
        data['message_id'] = event.message_id

    await Form.next()
    await event.reply("""
    Прежде чем приступить к процедуре отклика на вакансии, убедитесь, пожалуйста, что ваше резюме соответствует нашим обязательным требованиям:
1. Резюме должно быть на русском
2. Допустимый формат файла docx, pdf
3. Описание опыта работы: Месяц/год начала - месяц/год завершения
4. Описание опыта работы: Наименование проектов/компаний и должности/позиции
    """)
    await event.reply("Укажите ФИО кандидата")


@check_start
async def fio(event: types.Message, state: FSMContext, **kwargs):

    async with state.proxy() as data:
        data['name'] = event.text

    await Form.next()
    await event.reply("""
    Укажите локацию кандидата:
Город, если он в РФ
Страну, если за пределами РФ
    """)


@check_start
async def city(event: types.Message, state: FSMContext, **kwargs):

    async with state.proxy() as data:
        data['city'] = event.text

    await Form.next()

    buttons = (KeyboardButton('Junior'), KeyboardButton('Middle'), KeyboardButton('Middle+'), KeyboardButton('Senior'))

    kb = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, selective=True)
    kb.row(KeyboardButton('Junior'), KeyboardButton('Middle'), KeyboardButton('Middle+'), KeyboardButton('Senior'))
    # for btn in buttons:
    #     greet_kb.add(btn)

    await event.reply("Выберите уровень кандидата", reply_markup=kb)


@check_start
async def grade(event: types.Message, state: FSMContext, **kwargs):

    async with state.proxy() as data:
        data['grade'] = event.text

    await Form.next()
    await event.reply("Укажите рейт в час (можно указать в рублях или $)", reply_markup=ReplyKeyboardRemove())


@check_start
async def rate(event: types.Message, state: FSMContext, **kwargs):

    async with state.proxy() as data:
        data['rate'] = event.text

    await Form.next()
    await event.reply("Приложите резюме кандидата")


@check_start
async def resume(event: types.Message, state: FSMContext, **kwargs):

    if event.document is None:
        await event.reply("Приложите резюме кандидата")
        return

    file_id = event.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    name_parts = event.document.file_name.split('.')
    file_type = name_parts[-1]
    now = datetime.now()
    async with state.proxy() as data:
        file_name = f"{data['name']} {now.microsecond}"
    destination = f'shared_data/{file_name}.{file_type}'
    saved_file = await bot.download_file(file_path, destination)

    post_data = {'resume': destination}
    async with state.proxy() as data:
        post_data['vacancy_id'] = data['vacancy']
        post_data['name'] = data['name']
        post_data['city'] = data['city']
        post_data['grade'] = data['grade']
        post_data['rate'] = data['rate']
        post_data['partner'] = event.from_user.username
        post_data['message_id'] = data['message_id']

    url = f'{PROC_URL}resume/'
    async with ClientSession() as session:
        await session.post(url, json=post_data)

    await event.reply("Спасибо!")
    await state.finish()


async def echo(event: types.Message, state: FSMContext):
    # current_state = await state.get_state()
    # print(f'state {current_state} {state}')
    print('ECHO')
    print(event.chat)
    print(event.text)
    if event.text.startswith('/start'):
        await handle_start(event, state)
        return
    data = fetch_msg_data(event)
    if not data:
        return
    print(data.get('source'))
    # if data.get('source') in ('Потребности BSL', 'Kesmaty'):
    #     return
    url = get_url(data)
    async with ClientSession() as session:
        await session.post(url, json=data)


def get_url(data):
    if data.get('source') == 'TFAlliance':
        data['source'] = 'SmartSourcing'
        return f'{PROC_URL}actualize/'
    if data.get('source') == 'SkillStaff: новости и запросы на outstaff' and \
            (data.get('msg').startswith('#дайджест') or data.get('msg').startswith('Еженедельные запросы:')):
        return f'{PROC_URL}actualize/'
    if data.get('source') == 'SmartSourcing':
        if data.get('msg').startswith('🔴 Вакансия закрыта') or data.get('msg').startswith('🏁 Закрыт') or \
                data.get('msg').startswith('🙅‍♀️ Потребность закрыта') or \
                data.get('msg').startswith('❌ Потребность закрыта'):
            return f'{PROC_URL}close/'
        if data.get('msg').startswith('⏸Потребность на паузе') or \
                'Приостановлено рассмотрение' in data.get('msg'):
            return f'{PROC_URL}pause/'
        if 'Открытые вакансии #ТИМФОРС на' in data.get('msg'):
            return f'{PROC_URL}actualize/'
        if 'Открытые позиции ТИМ ФОРС' in data.get('msg'):
            return f'{PROC_URL}actualize/'
    if data.get('source') == 'SSP SOFT PARTNERS':
        if data.get('msg').startswith('Открытые позиции:'):
            return f'{PROC_URL}actualize/'
    return f'{PROC_URL}process/'


def remove_emoji(text):
    text = str(text)
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    res = emoji_pattern.sub(r'', text)
    return res


def fetch_msg_data(event: types.Message):
    if event.forward_from_chat:
        return {
            'source': event.forward_from_chat.full_name,
            'msg': event.text
        }

    if event.forward_from:
        if event.forward_from.first_name == 'Kesmaty':
            return {
                'source': event.forward_from.first_name,
                'msg': event.text
            }

    if event.text.startswith('Источник: '):
        reg_s = '(?<=Источник: ).*'
        reg = re.compile(reg_s)
        value = reg.findall(event.text)
        if not value:
            return

        value = value[0]
        value = value.strip()
        return {
            'source': value,
            'msg': event.text
        }


async def echo_vc(event: types.CallbackQuery):
    print('ECHO_VC')
    print(event)
    user_id = event.from_user.id
    text = 'ФИО кандидата'
    msg = await bot.send_message(user_id, text, parse_mode='MarkdownV2')
    print(msg)


async def start_bot():
    print('BOT_STARTED')
    global bot
    try:
        storage = MemoryStorage()
        disp = Dispatcher(bot=bot, storage=storage)
        # disp.register_message_handler(echo, content_types=ContentType.all())
        # disp.register_message_handler(echo, state='*')
        disp.register_message_handler(echo, state=None)
        disp.register_message_handler(fio, state=Form.name)
        disp.register_message_handler(city, state=Form.city)
        disp.register_message_handler(grade, state=Form.grade)
        disp.register_message_handler(rate, state=Form.rate)
        disp.register_message_handler(resume, content_types=[ContentType.DOCUMENT, ContentType.TEXT], state=Form.resume)
        disp.register_message_handler(registration_name, state=RegistrationForm.name)
        disp.register_message_handler(registration_company_name, state=RegistrationForm.company_name)
        disp.register_message_handler(registration_brand_name, state=RegistrationForm.brand_name)
        disp.register_message_handler(registration_country, state=RegistrationForm.country)
        disp.register_message_handler(registration_other_countries, state=RegistrationForm.other_countries)
        disp.register_message_handler(registration_inn, state=RegistrationForm.inn)
        disp.register_message_handler(registration_contact, state=RegistrationForm.contact)
        disp.register_message_handler(registration_email, state=RegistrationForm.email)
        # disp.register_message_handler(echo_file, content_types=ContentType.DOCUMENT, state=Form.resume)
        # disp.register_message_handler(echo_vc, commands=['button1'])
        disp.register_callback_query_handler(echo_vc, lambda c: c.data == 'button1')
        # disp.register_message_handler(echo_start, CommandStart)
        # disp.register_message_handler(echo_pic, content_types=ContentType.PHOTO)
        await disp.start_polling()
    finally:
        await bot.close()


routes = web.RouteTableDef()


@routes.get('/start_bot')
async def start(request):
    global BOT_IS_RUNNING
    if BOT_IS_RUNNING:
        return web.Response(text="bot is already running")
    BOT_IS_RUNNING = True
    event_loop = asyncio.get_event_loop()
    asyncio.ensure_future(start_bot(), loop=event_loop)
    return web.Response(text="bot is running")


@routes.post('/digest')
async def send_bot_digest(request):
    if not BOT_IS_RUNNING:
        return web.Response(text="bot is not running")
    data = await request.text()
    data = json.loads(data)
    # pprint(data)

    text = format_digest_msg(data)
    text = md.text(
        *text,
        sep='\n'
    )

    # text = data.get('msg')
    global bot
    # print(f'send {data["vacancy_id"]}')
    try:
        # print(f'new {data["vacancy_id"]}')
        msg = await bot.send_message(CHAT_ID, text, parse_mode='MarkdownV2')
    except RetryAfter as e:
        # print(f'SLEEP {data["vacancy_id"]} for {e.timeout}')
        await asyncio.sleep(e.timeout)
        # print(f'resend {data["vacancy_id"]}')
        msg = await bot.send_message(CHAT_ID, text, parse_mode='MarkdownV2')
    # pprint(f'msg info {msg}')
    data = {
        "message_id": msg.message_id,
        "chat_id": CHAT_ID,
    }
    # print(f'SLEEP {data["vacancy_id"]}')
    # await asyncio.sleep(1)
    return web.json_response(data)


@routes.post('/digest_partner_stop')
async def send_bot_digest_partner_stop(request):
    if not BOT_IS_RUNNING:
        return web.Response(text="bot is not running")
    data = await request.text()
    data = json.loads(data)
    # pprint(data)

    text = format_digest_partners_msg(data)
    text = md.text(
        *text,
        sep='\n'
    )

    # text = data.get('msg')
    global bot
    # print(f'send {data["vacancy_id"]}')
    try:
        # print(f'new {data["vacancy_id"]}')
        msg = await bot.send_message(CHAT_PARTNERS_ID, text, parse_mode='MarkdownV2')
    except RetryAfter as e:
        # print(f'SLEEP {data["vacancy_id"]} for {e.timeout}')
        await asyncio.sleep(e.timeout)
        # print(f'resend {data["vacancy_id"]}')
        msg = await bot.send_message(CHAT_PARTNERS_ID, text, parse_mode='MarkdownV2')
    # pprint(f'msg info {msg}')
    data = {
        "message_id": msg.message_id,
        "chat_id": CHAT_PARTNERS_ID,
    }
    # print(f'SLEEP {data["vacancy_id"]}')
    # await asyncio.sleep(1)
    return web.json_response(data)


@routes.post('/digest_partner_open')
async def send_bot_digest_partner_open(request):
    if not BOT_IS_RUNNING:
        return web.Response(text="bot is not running")
    data = await request.text()
    data = json.loads(data)
    # pprint(data)

    text = format_digest_partners_msg_open(data)
    text = md.text(
        *text,
        sep='\n'
    )

    # text = data.get('msg')
    global bot
    # print(f'send {data["vacancy_id"]}')
    try:
        # print(f'new {data["vacancy_id"]}')
        msg = await bot.send_message(CHAT_PARTNERS_ID, text, parse_mode='MarkdownV2')
    except RetryAfter as e:
        # print(f'SLEEP {data["vacancy_id"]} for {e.timeout}')
        await asyncio.sleep(e.timeout)
        # print(f'resend {data["vacancy_id"]}')
        msg = await bot.send_message(CHAT_PARTNERS_ID, text, parse_mode='MarkdownV2')
    # pprint(f'msg info {msg}')
    data = {
        "message_id": msg.message_id,
        "chat_id": CHAT_PARTNERS_ID,
    }
    # print(f'SLEEP {data["vacancy_id"]}')
    # await asyncio.sleep(1)
    return web.json_response(data)


def create_button(data):
    inline_btn_1 = InlineKeyboardButton(
        'Предложить кандидата',
        callback_data='button1',
        url=f'{BOT_URL}?start={data.get("vacancy_id")}'
    )
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
    return inline_kb1


@routes.post('/vacancy')
async def send_bot_vc(request):
    if not BOT_IS_RUNNING:
        return web.Response(text="bot is not running")
    data = await request.text()
    data = json.loads(data)
    pprint(data)

    text = format_vc_msg(data)
    text = md.text(
        *text,
        sep='\n'
    )

    global bot
    __chat_id = CHAT_PARTNERS_ID
    try:
        print(f'new {data["vacancy_id"]}')
        msg = await bot.send_message(__chat_id, text, parse_mode='MarkdownV2', reply_markup=create_button(data))
    except RetryAfter as e:
        print(f'SLEEP {data["vacancy_id"]} for {e.timeout}')
        await asyncio.sleep(e.timeout)
        print(f'resend {data["vacancy_id"]}')
        msg = await bot.send_message(__chat_id, text, parse_mode='MarkdownV2', reply_markup=create_button(data))
    data = {
        "message_id": msg.message_id,
        "chat_id": __chat_id,
    }
    return web.json_response(data)


@routes.post('/send_new')
async def send_bot_new(request):
    if not BOT_IS_RUNNING:
        return web.Response(text="bot is not running")
    data = await request.text()
    data = json.loads(data)
    # pprint(data)

    text = format_new_msg(data)
    text = md.text(
        *text,
        sep='\n'
    )

    # text = data.get('msg')
    global bot
    # print(f'send {data["vacancy_id"]}')
    try:
        print(f'new {data["vacancy_id"]}')
        msg = await bot.send_message(CHAT_ID, text, parse_mode='MarkdownV2')
    except RetryAfter as e:
        print(f'SLEEP {data["vacancy_id"]} for {e.timeout}')
        await asyncio.sleep(e.timeout)
        print(f'resend {data["vacancy_id"]}')
        msg = await bot.send_message(CHAT_ID, text, parse_mode='MarkdownV2')
    except MessageIsTooLong as e:
        print(f'MSG TOO LONG {data["vacancy_id"]}')
        data = {
            "message_id": 0,
            "chat_id": 0,
        }
        return web.json_response(data)
    else:
        # pprint(f'msg info {msg}')
        data = {
            "message_id": msg.message_id,
            "chat_id": CHAT_ID,
        }
        # print(f'SLEEP {data["vacancy_id"]}')
        # await asyncio.sleep(1)
        return web.json_response(data)


@routes.post('/send_change')
async def send_bot_change(request):
    if not BOT_IS_RUNNING:
        return web.Response(text="bot is not running")
    data = await request.text()
    data = json.loads(data)
    # pprint(data)

    text = format_change_msg(data)
    text = md.text(
        *text,
        sep='\n'
    )

    # text = data.get('msg')
    global bot
    # print(f'send {data["vacancy_id"]}')
    try:
        print(f'change {data["vacancy_id"]}')
        msg = await bot.send_message(CHAT_ID, text, parse_mode='MarkdownV2')
    except RetryAfter as e:
        print(f'SLEEP {data["vacancy_id"]} for {e.timeout}')
        await asyncio.sleep(e.timeout)
        print(f'resend {data["vacancy_id"]}')
        msg = await bot.send_message(CHAT_ID, text, parse_mode='MarkdownV2')
    # pprint(f'msg info {msg}')
    data = {
        "message_id": msg.message_id,
        "chat_id": CHAT_ID,
    }
    # print(f'SLEEP {data["vacancy_id"]}')
    # await asyncio.sleep(1)
    return web.json_response(data)


def format_digest_msg(data):
    today = date.today()
    msg_parts = [
        md.bold('#дайджест', 'от', today.isoformat()),
        ''
    ]
    for source, entity in data.items():
        msg_parts.append(md.bold(source))
        msg_parts.append('')
        for status, vacancies in entity.items():
            msg_parts.append(md.italic('  ', status))
            for vacancy in vacancies:
                msg_parts.append(md.escape_md('    ', vacancy.get('short_id'), vacancy.get('name')))
        msg_parts.append('')
    return msg_parts


def format_digest_partners_msg(data):
    today = date.today()
    msg_parts = [
        md.bold('#дайджест', 'от', today.isoformat()),
        ''
    ]
    for status, vacancies in data.items():
        msg_parts.append(md.italic('  ', status))
        for vacancy in vacancies:
            if msg_id := vacancy.get('msg_id'):
                value = md.link(vacancy.get('short_id'), f'https://t.me/c/1875910106/{msg_id}')
            else:
                value = vacancy.get('short_id')
            msg_parts.append(f"    {value} {md.escape_md(vacancy.get('name'))}")
            # msg_parts.append(md.escape_md('    ', vacancy.get('short_id'), vacancy.get('name')))
    msg_parts.append('')
    return msg_parts


def format_digest_partners_msg_open(data):
    today = date.today()
    msg_parts = [
        md.bold('#дайджест', 'от', today.isoformat()),
        md.bold('актуальный список открытых вакансий'),
        ''
    ]

    kinds = list(data.keys())
    kinds.sort()
    for kind in kinds:
        msg_parts.append(md.bold(kind))
        msg_parts.append('')
        entity = data[kind]
        types_ = list(entity.keys())
        types_.sort()
        for type_ in types_:
            msg_parts.append(md.italic('  ', type_))
            vacancies = entity[type_]
            vacancies.sort(key=lambda x: x.get('short_id'))
            for vacancy in vacancies:
                if msg_id := vacancy.get('msg_id'):
                    value = md.link(vacancy.get('short_id'), f'https://t.me/c/1875910106/{msg_id}')
                else:
                    value = vacancy.get('short_id')
                # msg_parts.append(md.escape_md('    ', value, vacancy.get('name')))
                # msg_parts.append(md.quote_html('    ', value, vacancy.get('name')))
                msg_parts.append(f"    {value} {md.escape_md(vacancy.get('name'))}")
        msg_parts.append('')
    return msg_parts


def format_change_msg(data):
    msg_parts = [
        md.italic('Вакансия', data.get('status')),
        md.escape_md(data.get('short_id')),
        md.bold(data.get('name')),
    ]

    section = []
    if value := data.get('project'):
        section.append(md.escape_md('Проект:', value))
    if value := data.get('source'):
        section.append(md.escape_md('Вакансия от', value))
    if value := data.get('manager'):
        value = value.split(', ')
        value = [f'@{x}' for x in value]
        value = ' '.join(value)
        section.append(md.escape_md('Ответственный по вакансии', value))
    if section:
        msg_parts.append('')
        msg_parts.extend(section)

    return msg_parts


def format_new_msg(data):
    msg_parts = [
        md.italic('Новая вакансия'),
        '',
        md.escape_md(data.get('short_id')),
        md.bold(data.get('name')),
    ]

    section = []
    if value := data.get('project'):
        section.append(md.escape_md('Проект:', value))
    if value := data.get('project_desc'):
        value = value.replace('проект:', '')
        value = value.strip()
        section.append(md.escape_md('Описание проекта:', value))
    if section:
        msg_parts.append('')
        msg_parts.extend(section)

    section = []
    if value := data.get('experience'):
        section.append(md.escape_md('Опыт:', value))
    if value := data.get('location'):
        section.append(md.escape_md('Локация:', value))
    if value := data.get('project_term'):
        section.append(md.escape_md('Срок проекта:', value))
    if value := data.get('rate'):
        curr_symb = '$' if data.get('rate_currency') == 'dollar' else '₽'
        value = f'{value}{curr_symb}'
        section.append(md.escape_md('Рейт:', value))
    if section:
        msg_parts.append('')
        msg_parts.extend(section)

    if value := data.get('tasks'):
        msg_parts.append('')
        msg_parts.append('Задачи:')
        msg_parts.append('')
        msg_parts.append(md.escape_md(value))

    if value := data.get('requirements'):
        msg_parts.append('')
        msg_parts.append('Требования:')
        msg_parts.append('')
        value = value.replace('требования:', '')
        value = value.strip()
        msg_parts.append(md.escape_md(value))

    if value := data.get('additional'):
        msg_parts.append('')
        msg_parts.append(md.escape_md(value))

    if value := data.get('manager'):
        value = value.split(', ')
        value = [f'@{x}' for x in value]
        value = ' '.join(value)
        msg_parts.append('')
        msg_parts.append(md.escape_md('Ответственный по вакансии', value))

    if value := data.get('source'):
        msg_parts.append('')
        msg_parts.append(md.escape_md('Вакансия от', value))

    if value := data.get('contact'):
        msg_parts.append(md.escape_md('Контакты менеджера:', value))

    return msg_parts


def format_vc_msg(data):
    msg_parts = [
        md.italic('Новая вакансия'),
        '',
        md.escape_md(data.get('short_id')),
        md.bold(data.get('name')),
    ]

    section = []
    if value := data.get('project'):
        section.append(md.escape_md('Проект:', value))
    if value := data.get('project_desc'):
        value = value.replace('проект:', '')
        value = value.strip()
        section.append(md.escape_md('Описание проекта:', value))
    if section:
        msg_parts.append('')
        msg_parts.extend(section)

    section = []
    if value := data.get('experience'):
        section.append(md.escape_md('Опыт:', value))
    if value := data.get('location'):
        section.append(md.escape_md('Локация:', value))
    if value := data.get('project_term'):
        section.append(md.escape_md('Срок проекта:', value))
    if value := data.get('partner_rate'):
        curr_symb = '$' if data.get('rate_currency') == 'dollar' else '₽'
        value = f'{value}{curr_symb}'
        section.append(md.escape_md('Рейт: до ', value))

    if section:
        msg_parts.append('')
        msg_parts.extend(section)

    if value := data.get('tasks'):
        msg_parts.append('')
        msg_parts.append('Задачи:')
        msg_parts.append('')
        msg_parts.append(md.escape_md(value))

    if value := data.get('requirements'):
        msg_parts.append('')
        msg_parts.append('Требования:')
        msg_parts.append('')
        value = value.replace('требования:', '')
        value = value.strip()
        msg_parts.append(md.escape_md(value))

    if value := data.get('manager'):
        value = value.split(', ')
        value = [f'@{x}' for x in value]
        value = ' '.join(value)
        msg_parts.append('')
        msg_parts.append(md.escape_md('Ответственный по вакансии', value))

    return msg_parts


@routes.post('/send_absence')
async def send_bot_change(request):
    if not BOT_IS_RUNNING:
        return web.Response(text="bot is not running")
    data = await request.text()
    data = json.loads(data)
    # pprint(data)

    text = data.get('text')
    # text = md.text(text)

    # text = data.get('msg')
    global bot
    # print(f'send {data["vacancy_id"]}')
    try:
        msg = await bot.send_message(CHAT_ID, text, parse_mode='MarkdownV2')
    except RetryAfter as e:
        print(f'SLEEP for {e.timeout}')
        await asyncio.sleep(e.timeout)
        msg = await bot.send_message(CHAT_ID, text, parse_mode='MarkdownV2')
    data = {
        "message_id": msg.message_id,
        "chat_id": CHAT_ID,
    }
    # print(f'SLEEP {data["vacancy_id"]}')
    # await asyncio.sleep(1)
    return web.json_response(data)


app = web.Application()
app.add_routes(routes)

web.run_app(app)
