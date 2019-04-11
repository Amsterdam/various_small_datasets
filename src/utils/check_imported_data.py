#!/usr/bin/env python
import psycopg2
import logging
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from various_small_datasets.settings import DATABASES

log = logging.getLogger(__name__)

database = DATABASES['default']
dbname = database['NAME']
user = database['USER']
password = database['PASSWORD']
host = database['HOST']
port = database['PORT']


def assert_count_zero():
    return lambda x: x[0][0] == 0


def assert_count_minimum(target):
    return lambda x: x[0][0] >= target


def all_valid_url(urls):
    url_validator = URLValidator()

    try:
        for url in urls:
            url_validator(url[0])
    except ValidationError as e:
        print(f"URL validation error for {url[0]}: ", e)
        return False
    return True


def do_checks(conn, sql_checks):
    with conn.cursor() as curs:
        for (name, sql, check) in sql_checks:
            print(f"check {name}")
            curs.execute(sql)
            result = curs.fetchall()
            if not check(result):
                print(f"Failed : {sql}")
                print(f"result : {result}")
                return False

    return True


def main(sql_checks):
    try:
        dsn = f"dbname='{dbname}' user='{user}' password='{password}' host='{host}' port={port}"
        with psycopg2.connect(dsn) as conn:
            result = do_checks(conn, sql_checks)
            if not result:
                exit(1)
    except psycopg2.Error as exc:
        print("Unable to connect to the database", exc)
        exit(1)

    print("All checks passed")
    exit(0)
