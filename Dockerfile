FROM python:3.6-buster
ENV PYTHONUNBUFFERED 1

ADD ./config /code/config
ADD ./sme_terceirizadas /code/sme_terceirizadas
ADD ./manage.py /code
ADD ./Pipfile /code/Pipfile
ADD ./Pipfile.lock /code/Pipfile.lock

WORKDIR /code
ENV PIP_NO_BINARY=:psycopg2:

RUN apt-get update && apt-get install \
    libpq-dev -y && \
    pip --no-cache-dir install -U pip && \
    pip --no-cache-dir install pipenv && \
    # https://stackoverflow.com/questions/46503947/how-to-get-pipenv-running-in-docker
    pipenv install --system --deploy --ignore-pipfile

CMD gunicorn config.wsgi:application --bind=0.0.0.0:8000 -w 8 && \
    celery -A config worker --loglevel=info --concurrency=3 -n worker1@%h && \
    celery -A config beat --loglevel=info --pidfile=/tmp/celeryd.pid

EXPOSE 8000
