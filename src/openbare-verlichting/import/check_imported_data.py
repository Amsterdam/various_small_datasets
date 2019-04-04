#!/usr/bin/env python
from utils.check_imported_data import main, assert_count_minimum

sql_checks = [
    ('count', "select count(*) from openbare_verlichting_new", assert_count_minimum(129410)),
]

if __name__ == '__main__':
    main(sql_checks)
