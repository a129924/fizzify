from typing import Literal

from pydantic import BaseModel
from typing_extensions import override


class ORMUrlBaseConfig(BaseModel):
    """Base class for ORM URL configuration."""

    driver: str
    database: str

    def generate_url(self) -> str:
        """Generate the URL for the ORM."""
        raise NotImplementedError


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
