import json
from django.test import TestCase, Client
from various_small_datasets.catalog.models import DataSet, DataSetField
from django.db import connection


class TestGenericApi(TestCase):

    def setUp(self):
        self.http_client = Client()

        # Setup test catalog
        ice_cream_parlours = DataSet(
            name='icp',
            table_name='icp_data',
            enable_api=True,
            name_field='naam',
            geometry_field='wkb_geometry',
            geometry_type='POINT',
            enable_geosearch=False,
            enable_maplayer=False,
        )
        ice_cream_parlours.save()

        DataSetField(name='id', db_column='icp_id', data_type='integer', primary_key=True,
                     dataset=ice_cream_parlours).save()
        DataSetField(name='naam', data_type='char', unique=True, dataset=ice_cream_parlours).save()
        DataSetField(name='prijs', data_type='integer', dataset=ice_cream_parlours).save()
        DataSetField(name='sterren', data_type='integer', dataset=ice_cream_parlours).save()
        DataSetField(name='smaken', data_type='char', dataset=ice_cream_parlours).save()
        DataSetField(name='locatie', db_column='wkb_geometry', data_type='geometry', dataset=ice_cream_parlours).save()

        create_table = '''
            create table icp_data (
            icp_id integer NOT NULL,
            naam character varying(128),
            prijs integer,
            sterren integer,
            smaken character varying(256),
            wkb_geometry geometry(Geometry,28992)
            )'''

        add_constraint = '''
        ALTER TABLE icp_data
        ADD CONSTRAINT icp_naam_unique UNIQUE(naam)'''

        create_index = '''
        CREATE INDEX icp_data_wkb_geometry_geom_idx
        ON icp_data USING gist(wkb_geometry);
        '''
        insert_data = '''
        INSERT INTO icp_data (icp_id, naam, prijs, sterren, smaken, wkb_geometry) VALUES
            (1, 'giraudi', 3, 4, 'pistache', ST_SetSRID(ST_MakePoint( 1000, 1000), 28992) ),
            (2, 'garone', 2, 3, 'sinaasappel', ST_SetSRID(ST_MakePoint( 2000, 2000), 28992) )
        '''
        with connection.cursor() as cursor:
            cursor.execute(create_table)
            cursor.execute(add_constraint)
            cursor.execute(create_index)
            cursor.execute(insert_data)

    def test_een(self):
        response = self.http_client.get('/vsd/icp/1/')
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result["id"] == 1
        assert result["naam"] == 'giraudi'
        assert result["smaken"] == 'pistache'

    def test_no_icp(self):
        response = self.http_client.get('/vsd/ipc/1/')
        assert response.status_code == 404

    def test_not_exist2(self):
        response = self.http_client.get('/vsd/icp/100/')
        assert response.status_code == 404
