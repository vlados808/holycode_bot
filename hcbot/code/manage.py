from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


TOKEN = "620850149:AAHmY3G1xlF2LFWBgCjTdfRQEiM4mz_Dx-o"


def init_django():
    import django
    from django.conf import settings

    if settings.configured:
        return

    settings.configure(
        INSTALLED_APPS=[
            'benchmark',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'postgres',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'HOST': 'db',
                'PORT': '5432',
            }
        }
    )
    django.setup()


def start(update, context):
    print(f'START {update.effective_chat.id}')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="I'm a bot, please talk to me!")


def echo(update, context):

    text = update.effective_message.text

    source_tg = update.effective_message.forward_from_chat.title
    print(f'SOURCE TG {source_tg}')
    from benchmark.models import Source
    try:
        source_db = Source.objects.get(pk=source_tg)
    except Source.DoesNotExist as e:
        print(f'source {source_tg} does not exist')
        return
    print(f'SOURCE DB {source_db}')
    source_db.parse_tg(text)


def start_bot():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    init_django()
    start_bot()
