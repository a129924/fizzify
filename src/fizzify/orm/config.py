from typing import Any, Literal

from pydantic import BaseModel, Field
from sqlalchemy.engine.interfaces import IsolationLevel
from typing_extensions import Self, override


class ORMEngineConfig(BaseModel):
    connect_args: dict[str, Any] | None = None
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_use_lifo: bool = True
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    isolation_level: IsolationLevel = "SERIALIZABLE"


class ORMEngineSqliteConfig(ORMEngineConfig):
    """
    Configuration for the SQLite ORM.
    """

    # is not support field
    max_overflow: int = Field(default=20, exclude=True)
    pool_timeout: int = Field(default=30, exclude=True)
    pool_use_lifo: bool = Field(default=True, exclude=True)

    isolation_level: IsolationLevel = "SERIALIZABLE"


class ORMEnginePostgresConfig(ORMEngineConfig):
    """
    Configuration for the PostgreSQL ORM.
    """

    isolation_level: IsolationLevel = "SERIALIZABLE"


class ORMEngineMssqlConfig(ORMEngineConfig):
    """
    Configuration for the SQL Server ORM.
    """

    isolation_level: IsolationLevel = "SERIALIZABLE"
    TrustServerCertificate: str = "yes"
    Encrypt: str = "no"
    driver_unicode_results: str = "True"


class ORMUrlBaseConfig(BaseModel):
    """Base class for ORM URL configuration."""

    database: str

    def generate_url(self) -> str:
        """Generate the URL for the ORM."""
        raise NotImplementedError


class ORMSqlServerConfig(ORMUrlBaseConfig):
    """
    Configuration for the SQL Server ORM.
    """

    driver: str = "mssql"
    engine: Literal["aioodbc", "pyodbc"] = "aioodbc"
    database: str  # DB
    user: str  # User
    password: str  # Password
    host: str  # IP
    port: int  # Port
    _schema: str  # Schema

    @classmethod
    def from_env(cls, path: str) -> Self:
        from dotenv import dotenv_values

        config = dotenv_values(path)

        return cls(
            engine=config["Engine"],  # type: ignore
            host=config["IP"],  # type: ignore
            port=int(config["Port"]),  # type: ignore
            database=config["DB"],  # type: ignore
            user=config["User"],  # type: ignore
            password=config["Password"],  # type: ignore
            _schema=config["Schema"],  # type: ignore
        )

    def get_odbc_driver(self) -> str:
        """
        Get the driver for the SQL Server ORM.

        drivers() = ['SQL Server', 'ODBC Driver 17 for SQL Server']
        """

        from pyodbc import drivers

        for driver in drivers():
            if driver.startswith("ODBC Driver") and driver.endswith("for SQL Server"):
                return driver.replace(" ", "+")

        raise ValueError("No SQL Server driver found")

    @override
    def generate_url(self) -> str:
        """
        Generate the URL for the SQL Server ORM.

        format:
        driver+engine://user:password@host:port/database?driver=ODBC+Driver+17+for+SQL+Server
        """
        return f"{self.driver}+{self.engine}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?driver={self.get_odbc_driver()}"


class ORMPostgresConfig(ORMUrlBaseConfig):
    """
    Configuration for the PostgreSQL ORM.
    format: driver+engine://user:pass@host:port/database

    Example:
    postgresql+asyncpg://myuser:mypassword@localhost:5432/mydatabase
    """

    driver: str = "postgresql"
    engine: Literal["asyncpg", "psycopg2"] = "asyncpg"
    database: str
    user: str
    password: str
    host: str
    port: int

    @override
    def generate_url(self) -> str:
        """Generate the URL for the PostgreSQL ORM."""
        return f"{self.driver}+{self.engine}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class ORMSqliteConfig(ORMUrlBaseConfig):
    """
    Configuration for the SQLite ORM.
    format: driver://user:pass@host/database

    if memory database, url is `driver:///:memory:`
    if file database on `absolute path`, url is `driver:///path/to/database.db`
    if file database on `relative path`, url is `driver://./path/to/database.db`
    """

    driver: str = "sqlite"
    database: str

    @override
    def generate_url(self) -> str:
        """Generate the URL for the SQLite ORM."""
        if self.database.startswith(":memory:"):
            # memory database
            return f"{self.driver}:///{self.database}"
        else:
            # file database
            return f"{self.driver}:///{self.database}.db"
