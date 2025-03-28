from collections.abc import Generator
from datetime import datetime

from pytest import fixture
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.fizzify.orm.config import ORMEngineMssqlConfig, ORMSqlServerConfig
from src.fizzify.orm.models.sync import SyncBase
from src.fizzify.orm.session.sync import SyncSessionManager
from src.fizzify.utils.orm import ORMUtils


class MssqlUser(SyncBase):
    name: Mapped[str] = mapped_column(String(255), primary_key=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


class MssqlUniqueUser(SyncBase):
    name: Mapped[str] = mapped_column(String(255), primary_key=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    __table_args__ = (UniqueConstraint("name"),)


@fixture
def mssql_config() -> ORMSqlServerConfig:
    return ORMSqlServerConfig.from_env("./config/mssql_db_connect.env")


@fixture
def mssql_engine_config() -> ORMEngineMssqlConfig:
    return ORMEngineMssqlConfig()


@fixture
def sync_session_manager(
    mssql_config: ORMSqlServerConfig, mssql_engine_config: ORMEngineMssqlConfig
) -> SyncSessionManager:
    return SyncSessionManager(config=mssql_config, engine_config=mssql_engine_config)


@fixture(scope="function")
def setup_database(
    sync_session_manager: SyncSessionManager,
) -> Generator[Session, None, None]:
    with sync_session_manager.get_session() as session:
        MssqlUser.__create_table__(sync_session_manager.engine)
        MssqlUniqueUser.__create_table__(sync_session_manager.engine)

        yield session

        MssqlUser.__delete_table__(sync_session_manager.engine)
        MssqlUniqueUser.__delete_table__(sync_session_manager.engine)


def test_drop_table(sync_session_manager: SyncSessionManager):
    with sync_session_manager.get_session() as session:
        MssqlUser.__delete_table__(sync_session_manager.engine)


def test_sql_name_is_mssql(sync_session_manager: SyncSessionManager):
    assert ORMUtils.get_driver_name(sync_session_manager.engine) == "mssql"


def test_sync_session(setup_database: Session):
    assert isinstance(setup_database, Session)


def test_sync_add(setup_database: Session):
    user = MssqlUser(name="John", age=20, created_at=datetime.now())

    user.save(setup_database)


def test_sync_find(setup_database: Session):
    user = MssqlUser(name="John", age=20, created_at=datetime.now())

    user.save(setup_database)

    found_user = MssqlUser.find_one(setup_database, filters=[MssqlUser.name == "John"])

    assert found_user == user


def test_sync_find_all(setup_database: Session):
    users = [
        MssqlUser(name="John", age=20, created_at=datetime.now()),
        MssqlUser(name="Jane", age=21, created_at=datetime.now()),
        MssqlUser(name="Doe", age=22, created_at=datetime.now()),
        MssqlUser(name="Alice", age=23, created_at=datetime.now()),
    ]

    for user in users:
        user.save(setup_database)

    found_users = MssqlUser.find_all(setup_database, filters=[MssqlUser.name == "John"])

    assert found_users[0] == users[0]


def test_sync_update(setup_database: Session):
    user = MssqlUser(name="John", age=20, created_at=datetime.now())

    user.save(setup_database)

    user.update(
        setup_database, filters=[MssqlUser.name == "John"], values={"name": "Jane"}
    )
    updated_user = MssqlUser.find_one(
        setup_database, filters=[MssqlUser.name == "Jane"]
    )

    assert updated_user is not None
    assert updated_user.name == "Jane"


def test_sync_delete(setup_database: Session):
    user = MssqlUser(name="John", age=20, created_at=datetime.now())

    user.save(setup_database)

    MssqlUser.delete_one(setup_database, filters=[MssqlUser.name == "John"])

    assert (
        MssqlUser.find_one(setup_database, filters=[MssqlUser.name == "John"]) is None
    )


def test_unique_user_insert_or_ignore(setup_database: Session):
    user = MssqlUniqueUser(name="John", age=20, created_at=datetime.now())

    user.save(setup_database)

    user2 = MssqlUniqueUser(name="Andrew", age=21, created_at=datetime.now())

    user2.insert_or_ignore(setup_database)

    assert (
        MssqlUniqueUser.find_one(
            setup_database, filters=[MssqlUniqueUser.name == "John"]
        )
        == user
    )

    filter_user2 = MssqlUniqueUser.find_one(
        setup_database, filters=[MssqlUniqueUser.name == "Andrew"]
    )
    assert filter_user2 is not None
    assert filter_user2.name == "Andrew"
    assert filter_user2.age == 21

    update_user2 = MssqlUniqueUser(name="Andrew", age=22, created_at=datetime.now())
    update_user2.insert_or_ignore(setup_database)

    filter_user2 = MssqlUniqueUser.find_one(
        setup_database, filters=[MssqlUniqueUser.name == "Andrew"]
    )
    assert filter_user2 is not None
    assert filter_user2.name == "Andrew"
    assert filter_user2.age == 21


def test_unique_user_insert_or_update(setup_database: Session):
    user = MssqlUniqueUser(name="John", age=20, created_at=datetime.now())

    user.save(setup_database)

    user1 = MssqlUniqueUser(name="John", age=21, created_at=datetime.now())
    user1.insert_or_update(setup_database)

    filter_user1 = MssqlUniqueUser.find_one(
        setup_database, filters=[MssqlUniqueUser.name == "John"]
    )
    assert filter_user1 is not None
    assert filter_user1.age == 21


def test_sync_get_except(setup_database: Session):
    user = MssqlUser(name="John", age=20, created_at=datetime.now())
    user.save(setup_database)

    unique_user = MssqlUniqueUser(name="John", age=20, created_at=datetime.now())
    unique_user2 = MssqlUniqueUser(name="Jane", age=21, created_at=datetime.now())
    unique_user.save(setup_database)
    unique_user2.save(setup_database)

    except_users = MssqlUniqueUser.get_except(
        setup_database,
        except_key1="name",
        cls2=MssqlUser,
        except_key2="name",
    )

    assert len(except_users) == 1
    assert except_users[0] == "Jane"
