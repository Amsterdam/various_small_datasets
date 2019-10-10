from various_small_datasets.interfaces.mapfile import types, serializers

MAP_FILE = """
MAP    NAME "test"    LAYER        NAME "test"        TYPE POINT        PROJECTION            "field from table"        END        CONNECTION "user=user password=pass dbname=dbname host=host"        CONNECTIONTYPE POSTGIS        CLASS            STYLE                SYMBOL "circlef"                SIZE 10                WIDTH 1                COLOR 255 0 0                OUTLINECOLOR 0 255 0            END        END        METADATA        END    END    PROJECTION        "init=epsg:4326"    END    WEB        METADATA            "a" "b"        END    ENDEND
"""

def test_normal():
    serializer = serializers.MappyfileSerializer()
    layer_class = types.FeatureClass()
    layer_class.add_style({
        'symbol': 'circlef',
        'size': 10,
        'width': 1,
        'color': [255, 0, 0],
        'outlinecolor': [0, 255, 0]
    })
    context = types.Mapfile(
        "test", [types.Layer(
            "test", "POINT", types.Connection.for_postgres(
                "user", "pass", "dbname", "host"),
            ["field from table"], classes=[layer_class]
        )],
        projection=["init=epsg:4326"],
        web=types.Web(types.Metadata({'a': 'b'}))
    )
    assert MAP_FILE.replace("\n", "") == serializer(context).replace("\n", "")