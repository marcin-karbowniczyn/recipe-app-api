FROM python:3.9-alpine3.13
LABEL mainteiner="Marcin Karbowniczyn"

ENV PYTHONUNBUFFERD 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
      build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
      then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    # -p makes sure all of the subdirectories will be created(vol, web, media)
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:dango-user /vol && \
    chmod -R 755 /vol


ENV PATH="/py/bin:$PATH"

USER django-user
