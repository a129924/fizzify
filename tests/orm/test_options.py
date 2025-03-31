from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.fizzify.orm.models.sync import SyncBase
from src.fizzify.orm.statement.options import SelectOptions


class OptionalUser(SyncBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)


def test_select_options():
    options = SelectOptions(
        mode="select",
        select_columns=[OptionalUser.name],
        filters=[OptionalUser.name == "test"],
        order_by=[OptionalUser.name.desc()],
    )

    assert options.mode == "select"
