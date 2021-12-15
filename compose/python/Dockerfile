FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH ${PYTHONPATH}:/app/manager/python

WORKDIR /app

RUN apt-get update \
    && apt-get install -y netcat postgresql gcc python3-dev musl-dev

COPY ./compose/python/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/python/start /start
RUN chmod +x /start

COPY app/requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT [ "/entrypoint" ]