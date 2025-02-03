from pytest import fixture

from src.fizzify.orm.config import ORMSqliteConfig


@fixture
def sqlite_config() -> ORMSqliteConfig:
    return ORMSqliteConfig(
        database=":memory:",
    )


def test_sqlite_config(sqlite_config: ORMSqliteConfig):
    assert sqlite_config.generate_url() == "sqlite:///:memory:"
