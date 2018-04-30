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
    ('count', "select count(*) from biz_view_new", lambda x: x[0][0] > 48),
    ('columns', """
select column_name from information_schema.columns where                                                                  
table_schema = 'public' and table_name = 'biz_data_new'
    """, lambda x: x == [("biz_id",), ("naam",), ("biz_type",), ("heffingsgrondslag",), ("website",), ("heffing",),
                         ("bijdrageplichtigen",), ("verordening",), ("wkb_geometry",)]),
    ('website', "select website from biz_view_new where website is not NULL", all_valid_url),
    ('verordening', "select verordening from biz_view_new where verordening is not NULL", all_valid_url),
    ('geometrie', """
select count(*) from biz_view where
geometrie is null or ST_IsValid(geometrie) = false or ST_GeometryType(geometrie) <> 'ST_Polygon'
    """,
     lambda x: x[0][0] == 0),
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
