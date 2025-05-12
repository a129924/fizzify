from src.fizzify.orm.config import ORMEngineConfig


def test_orm_config():
    config = ORMEngineConfig.from_file("tests/orm/test_config.json")
    assert config.isolation_level == "READ COMMITTED"
