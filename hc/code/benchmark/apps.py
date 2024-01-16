from django.apps import AppConfig


class BenchmarkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'benchmark'

    def ready(self):
        from .schedulers import start_job
        start_job()
