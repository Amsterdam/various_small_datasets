import math
import os
import pandas
import re


def main():
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)

    try:
        # Read Excel sheet in dataframe df
        df = pandas.read_excel('../data/Dataset BIZ v4.xlsx', sheet_name=1)

        # Read SQL data  in shape_map dictionary
        sql_path = '../tmp/BIZZONES.utf8.sql'
        sql_file = open(sql_path, 'r')
        sql = sql_file.readlines()
        shape_map = dict()
        for line in sql:
            m = re.search('INSERT INTO "public"\."bizzones" \("wkb_geometry" , "id1", "naam", "aktief", "ddingang".*\) '
            'VALUES \(\'([^\']+)\', (\d+), \'([^\']+)\', \'([^\']+)\', \'([^\']+)\'', line)
            if m:
                geometry, id1, naam, aktief, ddingang = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
                if aktief == 'Ja':
                    shape_map[naam] = (geometry, id1, ddingang, naam)

        # l = list(shape_map.keys())
        # l.sort()
        # print("\n".join(l) )

        # Add name mapping. This maps the name in the spreadsheet to the name in the shape file

        name_mapping = {
         'Albert Cuyp': 'AlbertCuypstraat',
         'Bedrijvencentrum Osdorp': 'BC Osdorp',
         'Beukenweg-Beukenplein': 'Beukenplein',
         'Cornelis Schuytstraat': 'Cor Schuijtstraat',
         'Damrak': 'Damrak_2017',
         'De Clercqstraat': 'De clercqstraat',
         'Eerste van der Helststraat': '1evdhelsttstraat',
         'Eerste van Swindenstraat': '1evSwindenstraat',
         'Ferdinand Bolstraat': 'Ferdinandbol_2017',
         'Haarlemmerbuurt 2e termijn': 'Haarlemmerstraat_2017',
         'Hoofddorpplein e.o.': 'Hoofddorppleinbuurt',
         'Jan Pieter Heijestraat': 'JP Heijerstraat',
         'Jodenbreestraat-Antoniesbreestraat': 'Jodebreestraat',
         'Kalverstraat-Heiligeweg eigenaren': 'KalverstraatOndernemers',
         'Kalverstraat-Heiligeweg gebruikers': 'KalverstraatOndernemers',
         'Knowledge Mile': 'Wibautstraat',
         'Olympiapleinbuurt': 'Olympiaplein',
         'Oostelijke Eilanden & Czaar Peterbuurt': 'CzaarPeter',
         'Osdorp Centrum': 'OsdorpCentrum',
         'Osdorper Ban eigenaren': 'OsdorperbanEigenaar',
         'Oud West': 'Eerste C Huygensstraat',
         'Prinsheerlijk': 'PrinsHeerlijk_2017',
         'Raadhuisstraat-Westermarkt': 'RaadhuisstraatWestermarkt',
         'Rembrandtplein/Thorbeckeplein': 'Rembrandtplein',
         'Rokin eigenaren': 'RokinOndernemers',
         'Rokin gebruikers': 'RokinOndernemers',
         'Rozengracht': 'Rozengracht_2017',
         'Spuistraat': 'SpuistraatEO',
         'Uitgaansgebied Leidsebuurt': 'Leidseplein',
         'Utrechtsestraat': 'Utrechtsestraat_2017',
         'Van Dam tot Stopera': 'Van Dam tot Stopera_2017',
         'Van Woustraat': 'V Woustraat',
         'Van der Helstplein': 'Vdhelstplein',
         'Warmoesstraat en omgeving': 'Warmoesstraat'
        }

        def find_geometry(name):
            m_name = name_mapping[name] if name in name_mapping else name
            return shape_map[m_name][0] if m_name in shape_map else None

        df['geometry'] = df['Naam BIZ'].apply(find_geometry)

        # df1 = df[['Naam BIZ', 'geometry']]
        # df1[df1['geometry'].isnull()]

        def makequotedlink(s):
            s = s.lstrip('#').rstrip('#')
            if not re.match('^https?://', s):
                s = 'http://' + s
            return "'" + s +  "'"

        # Create insert statements
        def makequote(s):
            return "'" + s + "'"

        def makesrid28992(s):
            return "ST_SetSRID('" + s + "'::geometry, 28992)"

        def make_insert(t):
            insert = '''insert into biz_data(
          biz_id  
        , naam
        , biz_type
        , heffingsgrondslag
        , website
        , heffing
        , bijdrageplichtigen
        , verordening
        , wkb_geometry) 
        values (
          {}
        , '{}'
        , '{}'
        , '{}'
        , {}
        , {}
        , {}
        , {}
        , {}
        );
        '''.format(t[0]
                   , t[1]
                   , t[3]
                   , t[4]
                   , 'NULL' if isinstance(t[5], float) and math.isnan(t[5]) else makequotedlink(t[5])
                   , 'NULL' if math.isnan(t[6]) else int(t[6])
                   , 'NULL' if math.isnan(t[7]) else int(t[7])
                   , makequotedlink(t[8])
                   , 'NULL' if t[9] is None else makesrid28992(t[9]))
            return insert


        inserts = []
        for t1 in df.itertuples():
            inserts.append(make_insert(t1))

        # Write file
        with open('biz_data_insert.sql', 'w') as f:
            f.write("\n".join(inserts))
        f.closed

    finally:
        os.chdir(current_dir)

if __name__ == '__main__':
    main()


