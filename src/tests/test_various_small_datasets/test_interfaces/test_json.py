from various_small_datasets.interfaces import json_


class IsolatedLoader(json_.JsonStrategicLoader):
    def _call_strategy(self, strategy, uri, **load_params):
        return strategy(uri, **load_params)

    def _call_parent(self, uri, **load_params):
        pass


def test_loader_isolated():
    loader = IsolatedLoader([lambda u, **l: 1])
    assert loader("bla") == 1


def test_loader_normal():
    loader = json_.JsonStrategicLoader(
        [lambda u, **p: '{{"a": "{}"}}'.format(u)]
    )
    assert loader("bla") == {'a': "bla"}


def test_loader_fallback():
    loader = json_.JsonStrategicLoader(
        [lambda u, **p: int(u)], {
            "uri": 10
        }
    )
    assert loader("uri") == 10


def test_load_normal():
    assert json_.load(
        1, 2, 3, lambda *l: list(l)
    ) == [1, 2, 3]