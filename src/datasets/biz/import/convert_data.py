import math
import pandas
import re
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sql_shape", type=str, help="SQL from Shape file")
    parser.add_argument("xlsx", type=str, help="XLSX spreadsheet")
    parser.add_argument("output", type=str, help="output file")
    args = parser.parse_args()

    try:
        # Read Excel sheet in dataframe df
        df = pandas.read_excel(args.xlsx)

        # Read SQL data  in shape_map dictionary
        sql_file = open(args.sql_shape, 'r')
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
            'A.J. Ernststraat': 'AJ Ernststraat',
            'Albert Cuyp': 'AlbertCuypstraat',
            'Albert Cuyp West': 'Albert Cuypstraat_2018',
            'Bedrijvencentrum Osdorp': 'BC Osdorp',
            'Beukenweg-Beukenplein': 'Beukenplein',
            'Caleido (Pieter Calandlaan)': 'Pieter Callandlaan',
            'Cornelis Schuytstraat': 'Cor Schuijtstraat',
            'Damrak': 'Damrak_2017',
            'De Clercqstraat': 'De clercqstraat',
            'Eerste van der Helststraat': '1evdhelsttstraat',
            'Eerste van Swindenstraat': '1evSwindenstraat',
            'Ferdinand Bolstraat': 'Ferdinandbol_2017',
            'Frans Halsbuurt': 'Frans Halsstraat',
            'Gerard Doustraat': 'Gerard Dou',
            'Haarlemmerbuurt 2e termijn': 'Haarlemmerstraat_2017',
            'Hoofddorpplein e.o.': 'Hoofddorppleinbuurt',
            'Jan Evertsenstraat ': 'J_Evertsen_2018',
            'Jan Pieter Heijestraat': 'JP Heijerstraat',
            'Jodenbreestraat-Antoniesbreestraat': 'Jodebreestraat',
            'Kalverstraat-Heiligeweg eigenaren': 'KalverstraatOndernemers',
            'Kalverstraat-Heiligeweg gebruikers': 'KalverstraatOndernemers',
            'Knowledge Mile': 'Wibautstraat',
            'Nieuwezijds Voorburgwal': 'NZVoorburgwal_2018',
            'Olympiapleinbuurt': 'Olympiaplein',
            'Oostelijke Eilanden & Czaar Peterbuurt': 'CzaarPeter',
            'Osdorp Centrum': 'OsdorpCentrum',
            'Osdorper Ban eigenaren': 'OsdorperbanEigenaar',
            'Oud West': 'Eerste C Huygensstraat',
            'Plein 40-45': 'Plein 40 45',
            'Prinsheerlijk': 'PrinsHeerlijk_2017',
            'Raadhuisstraat-Westermarkt': 'RaadhuisstraatWestermarkt',
            'Rembrandtplein/Thorbeckeplein': 'Rembrandtplein',
            'Rieker Business Park': 'Riekerpolder',
            'Rokin eigenaren': 'RokinOndernemers',
            'Rokin gebruikers': 'RokinOndernemers',
            'Rozengracht': 'Rozengracht_2017',
            'Spuistraat': 'SpuistraatEO',
            'The Olympic (Stadionplein)': 'Stadionplein',
            'Uitgaansgebied Leidsebuurt': 'Leidseplein',
            'Utrechtsestraat': 'Utrechtsestraat_2017',
            'Van Dam tot Stopera': 'Van Dam tot Stopera_2017',
            'Van Woustraat': 'V Woustraat',
            'Van der Helstplein': 'Vdhelstplein',
            'Warmoesstraat en omgeving': 'Warmoesstraat',
        }

        def find_geometry(name):
            m_name = name_mapping[name] if name in name_mapping else name
            return shape_map[m_name][0] if m_name in shape_map else None

        df['geometry'] = df['Naam BIZ'].apply(find_geometry)

        # df1 = df[['Naam BIZ', 'geometry']]
        # df1[df1['geometry'].isnull()]

        def makequotedlink(s):
            s = s.lstrip('#').rstrip('#')
            regex = re.compile(
                r'^(?:(?:http)s?://)?'  # http:// or https://
                r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)'  # domain...
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if not re.match(regex, s):
                print(f"Invalid URL: {s}")
                return ''

            if not re.match('^https?://', s):
                s = 'http://' + s
            return "'" + s + "'"

        def makesrid28992(s):
            return "ST_SetSRID('" + s + "'::geometry, 28992)"

        def make_insert(t):
            insert = '''insert into biz_data_new(
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
                   , t[2]
                   , t[3]
                   , 'NULL' if isinstance(t[4], float) and math.isnan(t[4]) else makequotedlink(t[4])
                   , 'NULL' if math.isnan(t[5]) else int(t[5])
                   , 'NULL' if math.isnan(t[6]) else int(t[6])
                   , makequotedlink(t[7])
                   , 'NULL' if t[8] is None else makesrid28992(t[8]))
            return insert

        inserts = []
        for t1 in df.itertuples():
            inserts.append(make_insert(t1))

        # Write file
        with open(args.output, 'w') as f:
            f.write("\n".join(inserts))

    except IOError as exc:
        print(exc)


if __name__ == '__main__':
    main()
