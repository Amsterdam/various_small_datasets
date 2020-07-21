import json
from django.test import TestCase, Client
from various_small_datasets.catalog.models import DataSet
from django.db import connection


class TestGenericApi(TestCase):

    def setUp(self):
        self.http_client = Client()

        # Setup test catalog
        ice_cream_parlours = DataSet(
            name='ijs',
            table_name='icp_data',
            enable_api=True,
            pk_field='icp_id',
            name_field='naam',
            geometry_field='wkb_geometry',
            geometry_type='POINT',
            enable_geosearch=False,
            enable_maplayer=False,
        )
        ice_cream_parlours.save()

        create_table = '''
create table icp_data (
icp_id integer NOT NULL PRIMARY KEY,
naam character varying(128),
prijs integer,
sterren integer,
smaken character varying(256),
wkb_geometry geometry(Geometry,28992),
datum date
            )'''

        add_constraint = '''
ALTER TABLE icp_data
ADD CONSTRAINT icp_naam_unique UNIQUE(naam)'''

        create_index = '''
CREATE INDEX icp_data_wkb_geometry_geom_idx
ON icp_data USING gist(wkb_geometry);
        '''
        insert_data = '''
INSERT INTO icp_data (icp_id, naam, prijs, sterren, smaken, wkb_geometry, datum) VALUES
(1, 'IJscuypje', 3, 4, 'pistache', ST_Transform(ST_GeomFromText('POINT(4.911880 52.367379)', 4326), 28992), null ),
(2, 'De ijsfiets', 2, 3, 'sinaasappel', ST_Transform(ST_GeomFromText('POINT(4.906130 52.365912)', 4326), 28992), '2020-01-01'),
(3, 'Het ijsboefje', 1, 4, 'straciatelli', ST_Transform(ST_GeomFromText('POINT(4.918146 52.358312)', 4326), 28992),  '2020-02-01');
        '''
        with connection.cursor() as cursor:
            cursor.execute(create_table)
            cursor.execute(add_constraint)
            cursor.execute(create_index)
            cursor.execute(insert_data)

    def test_een(self):
        response = self.http_client.get('/vsd/ijs/1/')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result["icp_id"] == 1
        assert result["naam"] == 'IJscuypje'
        assert result["smaken"] == 'pistache'

    def test_een_geojson(self):
        response = self.http_client.get('/vsd/ijs/1/?as_geojson')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert 'id' in result
        assert 'geometry' in result
        assert result['type'] == 'Feature'
        assert result["id"] == 1
        assert result['properties']["naam"] == 'IJscuypje'
        assert result['properties']["smaken"] == 'pistache'

    def test_all(self):
        response = self.http_client.get('/vsd/ijs/')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert '_links' in result
        assert 'results' in result
        assert len(result['results']) == 3

    def test_all_geojson(self):
        response = self.http_client.get('/vsd/ijs/?as_geojson')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert '_links' not in result
        assert 'results' not in result
        assert 'type' in result
        assert 'features' in result
        assert result['type'] == 'FeatureCollection'
        assert len(result['features']) == 3

    def test_naam(self):
        response = self.http_client.get('/vsd/ijs/?naam=boefje')
        assert response.status_code == 200
        result = json.loads(response.content)          
        assert len(result['results']) ==  1
        assert result['results'][0]['icp_id'] == 3
        assert result['results'][0]['naam'] == 'Het ijsboefje'
 
    def test_locatie(self):
        response = self.http_client.get('/vsd/ijs/?wkb_geometry=122233.8155281068, 486556.12919505127,100')
        assert response.status_code == 200
        result = json.loads(response.content) 
        assert len(result['results']) == 1
        assert result['results'][0]['icp_id'] == 2
        assert result['results'][0]['naam'] == 'De ijsfiets'

    def test_large_radius(self):
        response = self.http_client.get('/vsd/ijs/?wkb_geometry=52.365912,4.907598,2000')
        assert response.status_code == 400

    def test_no_icp(self):
        response = self.http_client.get('/vsd/ipc/1/')
        assert response.status_code == 404

    def test_not_exist2(self):
        response = self.http_client.get('/vsd/ijs/100/')
        assert response.status_code == 404

    def test_date_field_exact_match(self):
        response = self.http_client.get('/vsd/ijs/?datum=2020-01-01')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert len(result['results']) == 1
        assert result['results'][0]['naam'] == 'De ijsfiets'

    def test_date_field_lte(self):
        response = self.http_client.get('/vsd/ijs/?datum__lte=2020-01-02')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert len(result['results']) == 1
        assert result['results'][0]['naam'] == 'De ijsfiets'

    def test_date_field_gte(self):
        response = self.http_client.get('/vsd/ijs/?datum__gte=2020-01-01')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert len(result['results']) == 2
        assert result['results'][0]['naam'] == 'De ijsfiets'
        assert result['results'][1]['naam'] == 'Het ijsboefje'

    def test_date_field_incorrect_date_results_in_error(self):
        response = self.http_client.get('/vsd/ijs/?datum__gte=vandaag')
        assert response.status_code == 400
        result = json.loads(response.content)
        assert result == {'datum__gte': ['Enter a valid date/time.']}
