import re
from uuid import UUID


def extract_uuid(path: str, prefix: str) -> str:
    uuid_pattern = (
        r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"
    )
    pattern = rf"{re.escape(prefix)}_({uuid_pattern})"

    match = re.search(pattern, path)
    if not match:
        return None

    uuid_str = match.group(1)
    try:
        UUID(uuid_str)
        return uuid_str
    except ValueError:
        return None
