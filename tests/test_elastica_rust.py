import importlib


def test_rust_add():
    rust_mod = importlib.import_module("elastica_rust.elastica_rust")
    assert rust_mod.add_py(2, 3) == 5
