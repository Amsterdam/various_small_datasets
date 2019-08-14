#!/usr/bin/env python
from utils.check_imported_data import main, assert_count_minimum, assert_count_zero

sql_checks = [
    ('count', "select count(*) from overlastgebieden_new", assert_count_minimum(110)),
    ('columns', """
select column_name from information_schema.columns where                                                                  
table_schema = 'public' and table_name = 'overlastgebieden_new'
    """, lambda x: x == [('ogc_fid',), ('wkb_geometry',), ('oov_naam',), ('type',), ('url',)]),
    ('geometrie', """
select count(*) from overlastgebieden_new where
wkb_geometry is null or ST_IsValid(wkb_geometry) = false or ST_GeometryType(wkb_geometry) <> 'ST_Polygon'
    """,
     assert_count_zero()),
]

if __name__ == '__main__':
    main(sql_checks)
