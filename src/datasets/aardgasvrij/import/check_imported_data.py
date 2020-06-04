#!/usr/bin/env python
from shared.utils.check_imported_data import run_sql_checks, all_valid_url, assert_count_minimum, assert_count_zero

sql_checks = [
    ('count1', "select count(*) from buurten_new", assert_count_minimum(475)),
    ('kolom1', """
select count(column_name) from information_schema.columns where
 table_schema = 'public' and table_name = 'buurten_new' 
 and column_name in ('bu_naam', 'legenda', 'kookgas', 'wkb_geometry')
    """, assert_count_minimum(4)),
    ('geometrie1', """
select count(*) from buurten_new where
wkb_geometry is null or ST_IsValid(wkb_geometry) = false or ST_GeometryType(wkb_geometry) <> 'ST_MultiPolygon'
    """,
     assert_count_zero()),
    ('count2', "select count(*) from buurtinitiatieven_new", assert_count_minimum(50)),
    ('kolom2', """
select count(column_name) from information_schema.columns where
 table_schema = 'public' and table_name = 'buurtinitiatieven_new' 
 and column_name in ('bu_naam', 'buurtiniti', 'wkb_geometry')
    """, assert_count_minimum(3)),
    ('geometrie2', """
select count(*) from buurtinitiatieven_new where
wkb_geometry is null or ST_IsValid(wkb_geometry) = false or ST_GeometryType(wkb_geometry) <> 'ST_Point'
    """,
     assert_count_zero()),
]

if __name__ == '__main__':
    run_sql_checks(sql_checks)
