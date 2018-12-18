import argparse
import copy
import os.path
import pickle
import sys
import time
import json
import urllib.request
import urllib.parse


def convert_to_geojson(data):
    nodes = {}
    ways = {}
    start_nodes = {}
    relations = {}

    copyright1 = data['osm3s']['copyright']
    timestamp = data['osm3s']['timestamp_osm_base']

    elements = data['elements']
    for element in elements:
        id1 = element['id']
        type = element['type']
        if type == 'relation':
            relations[id1] = element
        elif type == 'way':
            ways[id1] = element
            start_nodes[element['nodes'][0]] = element
        elif type == 'node':
            nodes[id1] = element

    for rel_id, relation in relations.items():
        members = relation['members']
        relation['lines'] = {}
        relation['ways'] = {}
        relation['start_nodes'] = {}
        for member in members:
            if member['type'] == 'way':
                way_id = member['ref']
                way = copy.deepcopy(ways[way_id])
                relation['ways'][way_id] = copy.deepcopy(way)
                relation['start_nodes'][way['nodes'][0]] = way

        # combine way segments to longer lines
        for way_id, way in relation['ways'].items():
            if 'skip' in way:
                continue
            last_node = way['nodes'][-1]
            while last_node in relation['start_nodes']:
                way_next = relation['start_nodes'][last_node]
                nodes_next = way_next['nodes'][1:]
                way['nodes'].extend(nodes_next)
                id_next = way_next['id']
                relation['ways'][id_next]['skip'] = 1
                relation['start_nodes'].pop(last_node)
                last_node = way['nodes'][-1]
            relation['lines'][way_id] = way

    return {"type": "FeatureCollection",
            "properties": {
                "copyright": copyright1,
                "timestamp": timestamp
            },
            "features": [
                {
                    "type": "Feature",
                    "id": f"relation/{rel_id}",
                    "properties": {
                        "id": f"relation/{rel_id}",
                        "name": relation['tags']['name'],
                        "type": relation['tags']['type'],
                        "route": relation['tags']['route']
                    },
                    "geometry": {
                        "type": "MultiLineString",
                        "coordinates": [
                            [
                                [nodes[node]['lon'], nodes[node]['lat']] for node in way['nodes']
                            ] for way_id, way in relation['ways'].items()
                        ]
                    }
                } for rel_id, relation in relations.items()
            ]}



def get_static_data():
    datafile = f'/tmp/hoofdroutes.dat'

    if os.path.isfile(datafile) and time.time() - os.path.getmtime(datafile) < 24 * 60 * 60:
        fd = open(datafile, 'rb')
        result = pickle.load(fd)
        fd.close()
    else:
        data = f'[out:json];\n\n(\n relation[route~"truck|taxi"](52.35337677858021,4.868316650390625,52.39346332646216,4.936208724975586);\n);\n\nout body;\n>;\nout skel qt;'
        url = 'https://overpass-api.de/api/interpreter?data=' + urllib.parse.quote(data)
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))

        fw = open(datafile, 'wb')
        pickle.dump(result, fw)
        fw.close()

    return result


def makesrid28992(lat, lon):
    return f'ST_Transform(ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), 28992)'

def q(val):
    if val is None:
        return 'NULL'
    else:
        return f"'{val}'"

def make_insert(**kwargs):
    lat = kwargs.pop('latitude')
    lon = kwargs.pop('longitude')
    wkb_geometry = makesrid28992(lat, lon)
'''
    return insert
'''

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("output", type=str, help="output file")
    # args = parser.parse_args()

    result = get_static_data()
    # print(json.dumps(result, indent=4, sort_keys=True))
    geojson = convert_to_geojson(result)
    print(json.dumps(geojson, indent=4, sort_keys=True))


if __name__ == '__main__':
    main()
