import json

generic_importable = ["vastgoed", ]


def get_model_def(dataset):
    with open(f"datasets/{dataset}/meta/model.json") as json_file:
        return json.load(json_file)


def get_dataset_def(dataset):
    with open(f"datasets/{dataset}/meta/dataset.json") as json_file:
        return json.load(json_file)


def get_import_def(dataset):
    with open(f"datasets/{dataset}/meta/import.json") as json_file:
        return json.load(json_file)
