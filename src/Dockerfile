FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install git+https://github.com/amsterdam/objectstore.git

RUN mkdir -p /static && chown datapunt /static

COPY . ./

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=various_small_datasets.settings
RUN python manage.py collectstatic --noinput

CMD uwsgi
