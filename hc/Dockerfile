FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY ./code/ /code/
COPY ./docker-entrypoint.sh ./docker-entrypoint.sh
EXPOSE 8000
CMD python manage.py runserver 0.0.0.0:8000 --noreload
