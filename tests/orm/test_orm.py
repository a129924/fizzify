from pytest import fixture

from src.fizzify.orm.config import ORMSqliteConfig
from src.fizzify.orm.session.sync import SyncSessionManager


@fixture
def sqlite_config() -> ORMSqliteConfig:
    return ORMSqliteConfig(
        database=":memory:",
    )


@fixture
def sync_session_manager(sqlite_config: ORMSqliteConfig) -> SyncSessionManager:
    return SyncSessionManager(config=sqlite_config)


def test_sqlite_config(sqlite_config: ORMSqliteConfig):
    assert sqlite_config.generate_url() == "sqlite:///:memory:"


def test_sync_session(sync_session_manager: SyncSessionManager):
    from sqlalchemy.orm import Session

    with sync_session_manager.get_session() as session:
        assert isinstance(session, Session)
