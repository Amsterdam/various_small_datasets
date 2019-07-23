#!/usr/bin/env python
from utils.check_imported_data import main, assert_count_minimum

sql_checks = [
    ('count', "select count(*) from iot_device", assert_count_minimum(300)),
]

if __name__ == '__main__':
    main(sql_checks)
