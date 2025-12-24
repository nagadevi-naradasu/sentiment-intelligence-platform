def test_import_main():
    import main
    assert main is not None


def test_import_database():
    import database
    assert hasattr(database, "engine")


def test_import_models():
    import models
    assert hasattr(models, "Base")
