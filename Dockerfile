FROM python:3.8-buster
ENV PYTHONUNBUFFERED 1

ADD ./config /code/config
ADD ./sme_terceirizadas /code/sme_terceirizadas
ADD ./utility/__init__.py /code/utility/__init__.py
ADD ./utility/carga_dados /code/utility/carga_dados
ADD ./manage.py /code
ADD ./Pipfile /code/Pipfile
ADD ./Pipfile.lock /code/Pipfile.lock

WORKDIR /code
ENV PIP_NO_BINARY=:psycopg2:

RUN apt-get update && apt-get install -y libpq-dev && \
    pip install psycopg2 && \
    pip install xlsxwriter && \
    pip install pycparser && \
    pip --no-cache-dir install -U pip && \
    pip --no-cache-dir install pipenv==2022.4.8 && \
    # https://stackoverflow.com/questions/46503947/how-to-get-pipenv-running-in-docker
    pipenv install --system --deploy --ignore-pipfile

EXPOSE 8000
