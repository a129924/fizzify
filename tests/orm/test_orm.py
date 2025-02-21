from datetime import datetime

from pytest import fixture
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.fizzify.orm.config import ORMEngineSqliteConfig, ORMSqliteConfig
from src.fizzify.orm.models.sync import SyncBase
from src.fizzify.orm.session.sync import SyncSessionManager
from src.fizzify.utils.orm import ORMUtils


class User(SyncBase):
    name: Mapped[str]
    age: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


class UniqueUser(SyncBase):
    name: Mapped[str]
    age: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    __table_args__ = (UniqueConstraint("name"),)


@fixture
def sqlite_config() -> ORMSqliteConfig:
    return ORMSqliteConfig(
        dialect="sqlite",
        database=":memory:",
    )


@fixture
def sqlite_engine_config() -> ORMEngineSqliteConfig:
    return ORMEngineSqliteConfig()


@fixture
def sync_session_manager(
    sqlite_config: ORMSqliteConfig, sqlite_engine_config: ORMEngineSqliteConfig
) -> SyncSessionManager:
    return SyncSessionManager(config=sqlite_config, engine_config=sqlite_engine_config)


def test_sql_name_is_sqlite(sync_session_manager: SyncSessionManager):
    assert ORMUtils.get_driver_name(sync_session_manager.engine) == "sqlite"


def test_sqlite_config(sqlite_config: ORMSqliteConfig):
    assert sqlite_config.generate_url() == "sqlite:///:memory:"


def test_sync_session(sync_session_manager: SyncSessionManager):
    from sqlalchemy.orm import Session

    with sync_session_manager.get_session() as session:
        assert isinstance(session, Session)


def test_sync_add(sync_session_manager: SyncSessionManager):
    user = User(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)


def test_sync_find(sync_session_manager: SyncSessionManager):
    user = User(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)

        found_user = User.find_one(session, filters=[User.name == "John"])

        assert found_user == user


def test_sync_find_all(sync_session_manager: SyncSessionManager):
    users = [
        User(name="John", age=20, created_at=datetime.now()),
        User(name="Jane", age=21, created_at=datetime.now()),
        User(name="Doe", age=22, created_at=datetime.now()),
        User(name="Alice", age=23, created_at=datetime.now()),
    ]

    with sync_session_manager.get_session() as session:
        users[0].__create_table__(sync_session_manager.engine)
        for user in users:
            user.save(session)

        found_users = User.find_all(session, filters=[User.name == "John"])

        assert found_users[0] == users[0]


def test_sync_update(sync_session_manager: SyncSessionManager):
    user = User(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)

        user.update(session, filters=[User.name == "John"], values={"name": "Jane"})

        assert user.name == "Jane"


def test_sync_delete(sync_session_manager: SyncSessionManager):
    user = User(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)

        User.delete_one(session, filters=[User.name == "John"])

        assert User.find_one(session, filters=[User.name == "John"]) is None


def test_unique_user(sync_session_manager: SyncSessionManager):
    user = UniqueUser(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)

        user2 = UniqueUser(name="Andrew", age=21, created_at=datetime.now())

        user2.insert_or_ignore(session)

        assert UniqueUser.find_one(session, filters=[UniqueUser.name == "John"]) == user

        filter_user2 = UniqueUser.find_one(
            session, filters=[UniqueUser.name == "Andrew"]
        )
        assert filter_user2 is not None
        assert filter_user2.name == "Andrew"
        assert filter_user2.age == 21
