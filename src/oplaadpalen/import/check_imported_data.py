#!/usr/bin/env python
import psycopg2
import logging

from various_small_datasets.settings import DATABASES

log = logging.getLogger(__name__)

database = DATABASES['default']
dbname = database['NAME']
user = database['USER']
password = database['PASSWORD']
host = database['HOST']
port = database['PORT']

sql_checks = [
    ('count', "select count(*) from oplaadpalen_new", lambda x: x[0][0] >= 1354),
    ('geometrie', """
select count(*) from oplaadpalen_new where
wkb_geometry is null or ST_IsValid(wkb_geometry) = false or ST_GeometryType(wkb_geometry) <> 'ST_Point'
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
