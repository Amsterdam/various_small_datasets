import json

generic_importable = ["evenementen"]


def get_model_def(dataset):
    with open(f"{dataset}/meta/model.json") as json_file:
        return json.load(json_file)


def get_source_def(dataset):
    with open(f"{dataset}/meta/source.json") as json_file:
        return json.load(json_file)


def get_import_def(dataset):
    with open(f"{dataset}/meta/import.json") as json_file:
        return json.load(json_file)
