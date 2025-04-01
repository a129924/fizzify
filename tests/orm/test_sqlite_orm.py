from datetime import datetime

from pytest import fixture
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.fizzify.orm.config import ORMEngineSqliteConfig, ORMSqliteConfig
from src.fizzify.orm.models.sync import SyncBase
from src.fizzify.orm.session.sync import SyncSessionManager
from src.fizzify.utils.orm import ORMUtils


class FromSqliteUser(SyncBase):
    name: Mapped[str] = mapped_column(primary_key=True)
    age: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


class FromSqliteUniqueUser(SyncBase):
    name: Mapped[str] = mapped_column(primary_key=True)
    age: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    __table_args__ = (UniqueConstraint("name"),)


@fixture
def sqlite_config() -> ORMSqliteConfig:
    return ORMSqliteConfig(
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


def test_table_name_is_converted_to_lower(sync_session_manager: SyncSessionManager):
    assert FromSqliteUser.__tablename__ == "from_sqlite_user"
    assert FromSqliteUniqueUser.__tablename__ == "from_sqlite_unique_user"


def test_sql_name_is_sqlite(sync_session_manager: SyncSessionManager):
    assert ORMUtils.get_driver_name(sync_session_manager.engine) == "sqlite"


def test_sqlite_config(sqlite_config: ORMSqliteConfig):
    assert sqlite_config.generate_url() == "sqlite:///:memory:"


def test_sync_session(sync_session_manager: SyncSessionManager):
    from sqlalchemy.orm import Session

    with sync_session_manager.get_session() as session:
        assert isinstance(session, Session)


def test_sync_add(sync_session_manager: SyncSessionManager):
    user = FromSqliteUser(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)


def test_sync_find(sync_session_manager: SyncSessionManager):
    user = FromSqliteUser(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)

        found_user = FromSqliteUser.find_one(
            session, filters=[FromSqliteUser.name == "John"]
        )

        assert found_user == user


def test_sync_find_all(sync_session_manager: SyncSessionManager):
    users = [
        FromSqliteUser(name="John", age=20, created_at=datetime.now()),
        FromSqliteUser(name="Jane", age=21, created_at=datetime.now()),
        FromSqliteUser(name="Doe", age=22, created_at=datetime.now()),
        FromSqliteUser(name="Alice", age=23, created_at=datetime.now()),
    ]

    with sync_session_manager.get_session() as session:
        users[0].__create_table__(sync_session_manager.engine)
        for user in users:
            user.save(session)

        found_users = FromSqliteUser.find_all(
            session, filters=[FromSqliteUser.name == "John"]
        )

        assert found_users[0] == users[0]


def test_sync_update(sync_session_manager: SyncSessionManager):
    user = FromSqliteUser(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)

        user.update(
            session, filters=[FromSqliteUser.name == "John"], values={"name": "Jane"}
        )
        updated_user = FromSqliteUser.find_one(
            session, filters=[FromSqliteUser.name == "Jane"]
        )

        assert updated_user is not None
        assert updated_user.name == "Jane"


def test_sync_delete(sync_session_manager: SyncSessionManager):
    user = FromSqliteUser(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)

        FromSqliteUser.delete_one(session, filters=[FromSqliteUser.name == "John"])

        assert (
            FromSqliteUser.find_one(session, filters=[FromSqliteUser.name == "John"])
            is None
        )


def test_unique_user_insert_or_ignore(sync_session_manager: SyncSessionManager):
    user = FromSqliteUniqueUser(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)

        user2 = FromSqliteUniqueUser(name="Andrew", age=21, created_at=datetime.now())

        user2.insert_or_ignore(session)

        assert (
            FromSqliteUniqueUser.find_one(
                session, filters=[FromSqliteUniqueUser.name == "John"]
            )
            == user
        )

        filter_user2 = FromSqliteUniqueUser.find_one(
            session, filters=[FromSqliteUniqueUser.name == "Andrew"]
        )
        assert filter_user2 is not None
        assert filter_user2.name == "Andrew"
        assert filter_user2.age == 21

        update_user2 = FromSqliteUniqueUser(
            name="Andrew", age=22, created_at=datetime.now()
        )
        update_user2.insert_or_ignore(session)

        filter_user2 = FromSqliteUniqueUser.find_one(
            session, filters=[FromSqliteUniqueUser.name == "Andrew"]
        )
        assert filter_user2 is not None
        assert filter_user2.name == "Andrew"
        assert filter_user2.age == 21


def test_unique_user_insert_or_update(sync_session_manager: SyncSessionManager):
    user = FromSqliteUniqueUser(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        user.__create_table__(sync_session_manager.engine)
        user.save(session)

        user1 = FromSqliteUniqueUser(name="John", age=21, created_at=datetime.now())
        user1.insert_or_update(session)

        filter_user1 = FromSqliteUniqueUser.find_one(
            session, filters=[FromSqliteUniqueUser.name == "John"]
        )
        assert filter_user1 is not None
        assert filter_user1.age == 21


def test_sync_get_except(sync_session_manager: SyncSessionManager):
    unique_user = FromSqliteUniqueUser(name="John", age=20, created_at=datetime.now())
    unique_user2 = FromSqliteUniqueUser(name="Jane", age=21, created_at=datetime.now())
    user = FromSqliteUser(name="John", age=20, created_at=datetime.now())

    with sync_session_manager.get_session() as session:
        unique_user.__create_table__(sync_session_manager.engine)
        unique_user.save(session)
        unique_user2.save(session)

        user.__create_table__(sync_session_manager.engine)
        user.save(session)

        except_users = FromSqliteUniqueUser.get_except(
            session,
            keys1=[FromSqliteUniqueUser.name],
            keys2=[FromSqliteUser.name],
        )

        assert len(except_users) == 1
        assert except_users[0] == "Jane"


def test_sync_insert_many(sync_session_manager: SyncSessionManager):
    users = [
        FromSqliteUser(name="John", age=20, created_at=datetime.now()),
        FromSqliteUser(name="Jane", age=21, created_at=datetime.now()),
    ]

    with sync_session_manager.get_session() as session:
        users[0].__create_table__(sync_session_manager.engine)

        is_successes = FromSqliteUser.insert_many(session, users)
        assert is_successes

        found_users = FromSqliteUser.find_all(session)
        assert len(found_users) == 2
        assert found_users[0] == users[0]
        assert found_users[1] == users[1]
