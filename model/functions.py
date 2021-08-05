import typing

from pypika.terms import Function
from tortoise.expressions import F
from tortoise.fields.base import Field
from typing import Any
from enum import Enum


class ArrayAppend(Function):
    def __init__(self, field: str, value: typing.Any) -> None:
        if isinstance(value, Enum):
            value = value.value

        super().__init__("ARRAY_APPEND", F(field), str(value))


class ArrayRemove(Function):
    def __init__(self, field: str, value: typing.Any) -> None:
        if isinstance(value, Enum):
            value = value.value

        super().__init__("ARRAY_REMOVE", F(field), str(value))


class ArrayField(Field, list):
    def __init__(self, field: Field, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sub_field = field
        self.SQL_TYPE = "%s[]" % field.SQL_TYPE

    def to_python_value(self, value: Any) -> Any:
        return list(map(self.sub_field.to_python_value, value))

    def to_db_value(self, value: Any, instance: Any) -> Any:
        return [self.sub_field.to_db_value(val, instance) for val in value]
