#!/usr/bin/env python
import psycopg2
import logging

from various_small_datasets.settings import DATABASES
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

log = logging.getLogger(__name__)

database = DATABASES['default']
dbname = database['NAME']
user = database['USER']
password = database['PASSWORD']
host = database['HOST']
port = database['PORT']

val = URLValidator()


def all_valid_url(urls):
    try:
        for url in urls:
            val(url[0])
    except ValidationError as e:
        print(f"URL validation error for {url[0]}: ", e)
        return False
    return True


sql_checks = [
    ('count_metro', "select count(*) from trm_metro_new", lambda x: x[0][0] > 700),
    ('count_tram', "select count(*) from trm_tram_new", lambda x: x[0][0] > 4200),
    ('columns_tram', """
select column_name from information_schema.columns where table_schema = 'public' and table_name = 'trm_tram_new'
                    """, lambda x: {"ogc_fid", "wkb_geometry", "volgorde"} <= set(map(lambda y:y[0], x))),
    ('columns_metro', """
select column_name from information_schema.columns where table_schema = 'public' and table_name = 'trm_metro_new'
                    """, lambda x: {"ogc_fid", "wkb_geometry", "kge"} <= set(map(lambda y:y[0], x))),
]


def do_checks(conn):
    with conn.cursor() as curs:
        for (name, sql, check) in sql_checks:
            print(f"check {name}")
            curs.execute(sql)
            result = curs.fetchall()
            if not check(result):
                print(f"Failed : {sql}")
                return False

    return True


def main():
    try:
        dsn = f"dbname='{dbname}' user='{user}' password='{password}' host='{host}' port={port}"
        with psycopg2.connect(dsn) as conn:
            result = do_checks(conn)
            if not result:
                exit(1)
    except psycopg2.Error as exc:
        print("Unable to connect to the database", exc)
        exit(1)

    print("All checks passed")
    exit(0)


if __name__ == '__main__':
    main()
