# MapProxy configuration automatically generated from:
#   http://osm.omniscale.net/proxy/service
#
# NOTE: The generated configuration can be highly inefficient,
#       especially when multiple layers and caches are requested at once.
#       Make sure you understand the generated configuration!
#
# Created on 2019-09-26 12:38:01.139516 with:
# /usr/local/bin/mapproxy-util autoconfig \
#    --capabilities=http://mapserver/cgi- \
#    bin/mapserv?map=/map/generic.map \
#    --capabilities=http://osm.omniscale.net/proxy/service --output \
#    /mapproxy/mapproxy.yaml.tm --force

caches: {}
layers:
- layers:
  - name: osm
    sources: [osm_wms]
    title: OpenStreetMap (complete map)
  - name: osm_roads
    sources: [osm_roads_wms]
    title: OpenStreetMap (streets only)
  title: Omniscale OpenStreetMap WMS
services:
  wms:
    md:
      title: Omniscale OpenStreetMap WMS
sources:
  osm_roads_wms:
    coverage:
      bbox: [-180.0, -85.0511287798, 180.0, 85.0511287798]
      srs: EPSG:4326
    req:
      layers: osm_roads
      transparent: true
      url: http://osm.omniscale.net/proxy/service?
    supported_srs: ['CRS:84', 'EPSG:25831', 'EPSG:25832', 'EPSG:25833', 'EPSG:31466',
      'EPSG:31467', 'EPSG:31468', 'EPSG:3857', 'EPSG:4258', 'EPSG:4326', 'EPSG:900913']
    type: wms
  osm_wms:
    coverage:
      bbox: [-180.0, -85.0511287798, 180.0, 85.0511287798]
      srs: EPSG:4326
    req:
      layers: osm
      transparent: true
      url: http://osm.omniscale.net/proxy/service?
    supported_srs: ['CRS:84', 'EPSG:25831', 'EPSG:25832', 'EPSG:25833', 'EPSG:31466',
      'EPSG:31467', 'EPSG:31468', 'EPSG:3857', 'EPSG:4258', 'EPSG:4326', 'EPSG:900913']
    type: wms
