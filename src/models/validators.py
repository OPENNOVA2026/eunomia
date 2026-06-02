from datetime import date, datetime
from typing import Any
from uuid import UUID


def default(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return str(obj)
    if isinstance(obj, UUID):
        return str(obj)
    return obj.dict()
