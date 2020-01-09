from django.db import connection

from various_small_datasets.generic.model import get_model_repr, GeoFieldRepresentation
from various_small_datasets.utils.check_imported_data import do_checks, assert_count_minimum, assert_count_zero


def _get_check(import_def, model_def, check_type, check_props):
    table = f"{import_def['target']}_new"
    if check_type == 'count':
        if 'count_minimum' in check_props:
            count_method = assert_count_minimum(check_props['count_minimum'])
        else:
            raise NotImplementedError
        return [('count', f"select count(*) from {table}", count_method)]
    elif check_type == 'geometrie':
        model_repr = get_model_repr(model_def)
        geo_fields = [field for field in model_repr if isinstance(field, GeoFieldRepresentation)]

        collect_checks = []
        for field in geo_fields:
            if not field.allow_null:
                collect_checks.append((f'filled_geometrie_{field.field_name}',
                                       f"select count(*) from {table} where {field.field_name} is null",
                                       assert_count_zero()))
            collect_checks.append((f'valid_geometrie_{field.field_name}',
                                   f"select count(*) from {table} where ST_IsValid({field.field_name}) = false",
                                   assert_count_zero()))
            collect_checks.append((f'geometrie_type_{field.field_name}',
                                   f"select count(*) from {table} where "
                                   f"ST_GeometryType({field.field_name}) <> '{field.psql_type}'",
                                   assert_count_zero()))
        return collect_checks
    else:
        raise NotImplementedError


def check_import(import_def, model_def):
    sql_checks = []
    for k, v in import_def['check'].items():
        sql_checks.extend(_get_check(import_def, model_def, k, v))
    all_checks_pass = do_checks(connection, sql_checks)
    if not all_checks_pass:
        raise RuntimeError("Import aborted, due too failing checks")
