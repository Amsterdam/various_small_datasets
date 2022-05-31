FROM amsterdam/python:3.8.7-buster
LABEL maintainer=datapunt@amsterdam.nl

RUN sed -i '/^mozilla\/AddTrust_External_Root.crt/c\!mozilla\/AddTrust_External_Root.crt' /etc/ca-certificates.conf
RUN update-ca-certificates

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install git+https://github.com/amsterdam/objectstore.git

RUN mkdir -p /static && chown datapunt /static

COPY . ./

USER datapunt

ENV DJANGO_SETTINGS_MODULE=various_small_datasets.settings DJANGO_DEBUG=false
RUN python manage.py collectstatic --noinput

CMD uwsgi
