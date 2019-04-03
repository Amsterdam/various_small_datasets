from abc import ABC, abstractmethod

from django.contrib.gis.db import models as geo_models
from django.db import models

from various_small_datasets.generic.catalog import get_model_def


class FieldRepresentation(ABC):

    def __init__(self, field_name, **field_def):
        self.field_name = field_name
        self.field_type = field_def['type']
        self.field_props = field_def.get('properties', {})

    @property
    def allow_null(self):
        return self.field_props.get('null', True)

    @property
    def with_index(self):
        return self.field_props.get('index', False)

    @property
    def is_unique(self):
        return self.field_props.get('unique', False)

    @property
    def is_pk(self):
        return self.field_props.get('primary_key', False)

    @property
    def is_name_field(self):
        return self.field_props.get('text_find', False)

    @property
    def is_geo_field(self):
        return self.field_props.get('geo_find', False)

    @property
    @abstractmethod
    def django(self):
        pass

    @property
    @abstractmethod
    def psql(self):
        pass

    def psql_index(self, table):
        if not self.with_index:
            return ""
        unique_s = "UNIQUE" if self.is_unique else ""
        return f"CREATE {unique_s} INDEX {table}_{self.field_name}__idx ON {table} ({self.field_name});\n"


class GeoFieldRepresentation(FieldRepresentation, ABC):
    psql_type = 'ST_Geometry'
    geo_type = 'GEOMETRY'

    def psql_index(self, table):
        if not self.with_index:
            return ""
        return f"CREATE INDEX {table}_{self.field_name}__gix ON {table} USING GIST ({self.field_name});\n"

    @property
    @abstractmethod
    def psql_type(self):
        pass


class SERIAL(FieldRepresentation):

    @property
    def django(self):
        return None

    @property
    def psql(self):
        return f"{self.field_name} SERIAL"


class Char(FieldRepresentation):

    @property
    def django(self):
        dfield_props = {'null': self.allow_null}
        if 'length' in self.field_props:
            dfield_props['max_length'] = self.field_props['length']
        if self.is_pk:
            dfield_props['primary_key'] = True
        return models.CharField(**dfield_props)

    @property
    def psql(self):
        length_s = f"({self.field_props['length']})" if 'length' in self.field_props else ""
        return f"{self.field_name} CHARACTER VARYING{length_s}"


class URL(Char):

    @property
    def django(self):
        return models.URLField()


class Text(FieldRepresentation):

    @property
    def django(self):
        return models.TextField()

    @property
    def psql(self):
        return f"{self.field_name} text"


class Date(FieldRepresentation):

    @property
    def django(self):
        return models.DateField()

    @property
    def psql(self):
        return f"{self.field_name} date"


class Point(GeoFieldRepresentation):
    psql_type = 'ST_Point'
    geo_type = 'POINT'

    @property
    def django(self):
        return geo_models.PointField(srid=self.field_props.get('srid', 28992))

    @property
    def psql(self):
        return f"{self.field_name} geometry(Point, {self.field_props.get('srid', 28992)})"


class Time(FieldRepresentation):

    @property
    def django(self):
        return models.TimeField()

    @property
    def psql(self):
        return f"{self.field_name} time without time zone"


def represent_field(field_name, field_def):
    if field_def['type'] == "SERIAL":
        return SERIAL(field_name, **field_def)
    elif field_def['type'] == "String":
        return Char(field_name, **field_def)
    elif field_def['type'] == "URL":
        return URL(field_name, **field_def)
    elif field_def['type'] == "Text":
        return Text(field_name, **field_def)
    elif field_def['type'] == "Date":
        return Date(field_name, **field_def)
    elif field_def['type'] == "Time":
        return Time(field_name, **field_def)
    elif field_def['type'] == "Geo.Point":
        return Point(field_name, **field_def)
    else:
        raise NotImplementedError


def get_model_repr(model_def, with_internal=True):
    def _is_internal_field(field_def):
        if 'internal' not in field_def.get('properties', {}):
            return False
        return field_def['properties']['internal']

    return [represent_field(k, v) for k, v in model_def.items() if with_internal or not _is_internal_field(v)]


def get_django_model(model_name, model_def, new_table=False):
    model_repr = get_model_repr(model_def, with_internal=False)
    django_model_attrs = {f.field_name: f.django for f in model_repr}
    django_model_attrs['Meta'] = type('Meta', (object,), {
        'managed': False,
        'db_table': (f"{model_name}_new" if new_table else model_name),
        'ordering': [get_pk(model_def).field_name]
    })
    django_model_attrs['__str__'] = lambda self: getattr(self, get_name_field(model_def).field_name)
    django_model_attrs['get_id'] = lambda self: getattr(self, get_pk(model_def).field_name)
    django_model_attrs['__module__'] = 'various_small_datasets.gen_api.models'
    return type(model_name.upper() + 'Model', (models.Model,), django_model_attrs)


def get_serial(model_def):
    return [field for field in (get_model_repr(model_def)) if isinstance(field, SERIAL)][0]


def get_pk(model_def):
    return [field for field in (get_model_repr(model_def)) if field.is_pk][0]


def get_name_field(model_def):
    return [field for field in (get_model_repr(model_def)) if field.is_name_field][0]


def get_geo_field(model_def):
    return [field for field in (get_model_repr(model_def)) if field.is_geo_field][0]


def get_django_model_by_name(dataset_name):
    model_def = get_model_def(dataset_name)
    return get_django_model(dataset_name, model_def)
