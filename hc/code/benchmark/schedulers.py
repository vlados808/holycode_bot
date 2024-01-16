from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from .models import Source
from constance import config


def background_job():
    now = datetime.now()
    if now.weekday() in (5, 6):
        return

    print(now.hour, now.minute, config.GS_PARSING_TIME.hour, config.GS_PARSING_TIME.minute)
    if now.hour == config.GS_PARSING_TIME.hour and now.minute - config.GS_PARSING_TIME.minute < 5:
        sources = Source.objects.filter(type='google sheet')
        for source in sources:
            print(source)
            source.actualize()

    # sources = Source.objects.filter(type='google sheet')
    # for source in sources:
    #     print(source)
    #     source.actualize()


def start_job():
    print('START JOB')
    scheduler = BackgroundScheduler()
    # scheduler.add_job(background_job, 'interval', seconds=5)
    # scheduler.add_job(actualize_google_sources, 'interval', hours=24)
    scheduler.start()
