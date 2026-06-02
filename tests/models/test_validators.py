from datetime import date, datetime
from uuid import uuid4

import pytest

from src.models.validators import default


def test_default_with_datetime():
    dt = datetime(2023, 5, 17, 15, 30)
    result = default(dt)
    assert result == dt.isoformat()


def test_default_with_date():
    d = date(2023, 5, 17)
    result = default(d)
    assert result == str(d)


def test_default_with_uuid():
    u = uuid4()
    result = default(u)
    assert result == str(u)


def test_default_with_custom_object():
    class Custom:
        def dict(self):
            return {"foo": "bar"}

    obj = Custom()
    result = default(obj)
    assert result == {"foo": "bar"}


def test_default_with_invalid_object_raises():
    class NoDict:
        pass

    obj = NoDict()
    with pytest.raises(AttributeError):
        default(obj)
