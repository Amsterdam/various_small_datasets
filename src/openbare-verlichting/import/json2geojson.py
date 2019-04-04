#! /usr/bin/env python
import logging
from sys import argv
import simplejson as json
from geojson import Point

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


OBJECT_TYPES = {
    'Klok': '1',
    'Overspanning': '2',
    'Gevel_Armatuur': '3',
    'Lichtmast': '4',
    'Grachtmast': '5',  # Old style light posts next to the "grachten"
}

TYPES_OBJECT = {v: k for k, v in OBJECT_TYPES.items()}  # inverted mapping


def json2geojson(data):
    skip_cnt = 0

    features = []
    for element in data:
        objecttype_id = element.get('objecttype')
        if objecttype_id == OBJECT_TYPES['Klok']:
            skip_cnt += 1
            continue

        geometry = Point((element.get('lon'), element.get('lat')), srid=4326)

        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                'type': TYPES_OBJECT[objecttype_id],
                'objectnummer': element['objectnummer'],
            },
        })

    log.info(f'skipped importing {skip_cnt} objects')
    log.info(f'features count {len(features)} objects')

    geojson = {
        "type": "FeatureCollection",
        "features": [f for f in features]
    }
    return geojson


if __name__ == '__main__':
    script, in_file, out_file = argv
    data = json.load(open(in_file))
    geojson = json2geojson(data)
    output = open(out_file, 'w')

    log.info(f'writing output...')
    json.dump(geojson, output)
    log.info(f'done')
