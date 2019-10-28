FROM python:3.6-alpine3.8
ENV PYTHONUNBUFFERED 1

ADD ./config /code/config
ADD ./sme_terceirizadas /code/sme_terceirizadas
ADD ./manage.py /code
ADD ./requirements /code/requirements
ADD ./Pipfile /code/Pipfile
ADD ./Pipfile.lock /code/Pipfile.lock

WORKDIR /code
ENV PIP_NO_BINARY=:psycopg2:

RUN apk update && apk add --no-cache \
      --virtual=.build-dependencies \
      postgresql-dev \
      tzdata \
      gcc \
      musl-dev \
      python3-dev \
      jpeg-dev \
      # Pillow
      zlib-dev \
      freetype-dev \
      lcms2-dev \
      openjpeg-dev \
      tiff-dev \
      tk-dev \
      tcl-dev \
      harfbuzz-dev \
      fribidi-dev && \
    pip --no-cache-dir install -U pip && \
    pip --no-cache-dir install pipenv && \
    # https://stackoverflow.com/questions/46503947/how-to-get-pipenv-running-in-docker
    pipenv install --system --deploy --ignore-pipfile && \
    cp /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    apk add libpq && \
    apk del --purge .build-dependencies && \
    rm -rf /var/cache/apk/* && \
    rm -rf /root/.cache

EXPOSE 8000
