import pandas as pd
import re
import argparse

import pprint
pp = pprint.PrettyPrinter()

# Configuration
SHEET_NAME = "Achterkant"
PROPERTIES = [
    ('Theme', ['Thema', 'Subthema 1', 'Subthema 2']),
    ('Area', ['Stadsdeel']),
    ('Type', ['Type.']),
    ('Level', ['Niveau ']),
    ('Source', ['(bestuurlijke)  bron '])
]
TEXT = "Kerntekst"
DESCRIPTION = "Toelichting"

ITEMS_TABLE = "hior_items_new"
PROPS_TABLE = "hior_properties_new"

def import_file(filename):

    # xl = pd.ExcelFile(FILENAME)
    # sheets = xl.sheet_names

    items = []
    properties = []

    df = pd.read_excel(filename, sheet_name=SHEET_NAME)
    # columns = df.axes[1]

    # pp.pprint(sheets)
    # pp.pprint(columns)

    for row in df.iterrows():
        id, series = row

        # Add 2 to id because lines start at 1. Index starts at 0 and 1 line if for the header
        id = id + 2
        text = "" if pd.isnull(series[TEXT]) else series[TEXT]
        description = "" if pd.isnull(series[DESCRIPTION]) else series[DESCRIPTION]

        if len(text) == 0:
            # Skip lines with empty TEXT field
            pp.pprint(f'Warning: line {id} - Missing {TEXT}')
            continue

        item_properties = []
        for (name, keys) in PROPERTIES:
            values = [series[key] for key in keys]
            for value in [value for value in values if not pd.isnull(value)]:
                item_properties.append({"item_id": id, "name": name, "value": value})


        # Post process
        for property in item_properties:
            value = property["value"]
            if property["name"] == "Level":
                value = re.sub(r'^\d\. ', '', value)
            value = value.title().strip()
            property["value"] = value

        isValid = True
        for (name, _) in PROPERTIES:
            props = [property["value"] for property in item_properties if property["name"] == name]
            isPropValid = len(props) > 0
            if not isPropValid:
                pp.pprint(f'Warning: line {id} - Missing property {name}')
                isValid = False

        if isValid:
            items.append({"id": id, "text": text, "description": description})
            properties = properties + item_properties

    for (name, _) in PROPERTIES:
        values = set([property["value"] for property in properties if property["name"] == name])
        pp.pprint(f'{name} - {len(values)} values')

    pp.pprint(f'Total items {len(items)}')
    pp.pprint(f'Total properties {len(properties)}')
    return (items, properties)


def get_value(item, field):
    value = item[field]
    if isinstance(value, str):
        value = value.replace("'", "\"")
        value = f"'{value}'"
    return str(value)

def write_inserts(out_dir, items, properties):
    for (collection, table_name) in [(items, ITEMS_TABLE), (properties, PROPS_TABLE)]:
        with open(f"{out_dir}/{table_name}.sql", "w") as f:
            fields = collection[0].keys()
            f.write(f"""
INSERT INTO {table_name}
    ({', '.join(fields)})
VALUES""")
            for i, item in enumerate(collection):
                values = [get_value(item, field) for field in fields]
                f.write(f"""{"," if i > 0 else ""}
    ({', '.join(values)})""")
            f.write(";")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_xls", type=str, help="Excel file to process")
    parser.add_argument("out_dir", type=str, help="Output directory for resulting SQL import files")
    args = parser.parse_args()

    items, properties = import_file(args.input_xls)
    write_inserts(args.out_dir,  items, properties)


if __name__ == '__main__':
    main()
