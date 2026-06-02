from typing import Optional

import requests

from src.settings import settings


def __post(json: dict):
    url = f"{settings.external_url}"
    response = requests.post(url, json=json)

    if not response.ok:
        message = f"Service responded with a {response.status_code} status code"
        raise Exception(message)


def notify_raw_documents_analyzed(
    input_file: str,
    status: str = "ok",
    files: list[str] = None,
    detail: Optional[str] = None,
):
    json_payload = {"input_file": input_file, "status": status}

    if files:
        json_payload["files"] = files
    if detail:
        json_payload["detail"] = detail

    __post(json_payload)
