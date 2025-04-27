FROM python:3.12

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

COPY ../app /code/app

ENV PYTHONPATH=/code/app:/code/app

WORKDIR /code/app

CMD uvicorn app.main:app --host "0.0.0.0" --port $APP_PORT
