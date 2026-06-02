import json
from unittest.mock import MagicMock, patch

import pytest

from src.tasks import process_s3_raw_documents


@pytest.fixture
def mock_parser():
    parser = MagicMock()
    parser.normalize_raw_document.side_effect = lambda doc: {
        "id": doc["id"],
        "type": "post",
    }  # noqa: E501
    parser.get_document_interactions.side_effect = lambda doc: [
        {"id": f"{doc['id']}_int"}
    ]  # noqa: E501
    return parser


def test_process_s3_raw_documents_success(mock_parser):
    input_file = "telegram/somefile.jsonl"
    output_folder = "normalized/telegram"
    silent = False
    normalized_documents_bucket = "normalized-docs-bucket"

    raw_data = [
        json.dumps({"id": "1"}),
        json.dumps({"id": "2"}),
    ]
    raw_file_bytes = "\n".join(raw_data).encode("utf-8")

    # Mocks
    with (
        patch("src.tasks.get_file_parser", return_value=mock_parser),
        patch("src.tasks.s3_client.download_fileobj") as mock_download,
        patch("src.tasks.s3_client.upload_fileobj") as mock_upload,
        patch("src.tasks.notify_raw_documents_analyzed") as mock_notify,
        patch.multiple(
            "src.tasks.settings",
            aws_s3_output_bucket=normalized_documents_bucket,
        ),
    ):
        # Simulate S3 download by writing data to the provided fileobj
        def fake_download(bucket, key, fileobj):
            fileobj.write(raw_file_bytes)
            fileobj.seek(0)

        mock_download.side_effect = fake_download

        # Run task
        process_s3_raw_documents(input_file, output_folder, silent)

        assert mock_download.called
        assert mock_upload.call_count == 2

        if not silent:
            mock_notify.assert_called_once()
            notify_args = mock_notify.call_args[1]
            assert notify_args["files"] == [
                f"{output_folder}/posts.jsonl",
                f"{output_folder}/interactions.jsonl",
            ]


def test_process_s3_raw_documents_error_triggers_notification():
    input_file = "telegram/invalid.jsonl"
    output_folder = "normalized/telegram"
    silent = False

    with (
        patch("src.tasks.get_file_parser", side_effect=RuntimeError("Parser failed")),
        patch("src.tasks.notify_raw_documents_analyzed") as mock_notify,
    ):
        process_s3_raw_documents(input_file, output_folder, silent)

        mock_notify.assert_called_once()
        args = mock_notify.call_args[1]
        assert args["status"] == "error"
        assert "Parser failed" in args["detail"]


def test_process_s3_raw_documents_silent_error_does_not_notify():
    input_file = "telegram/invalid.jsonl"
    output_folder = "normalized/telegram"
    silent = True

    with (
        patch("src.tasks.get_file_parser", side_effect=RuntimeError("Parser failed")),
        patch("src.tasks.notify_raw_documents_analyzed") as mock_notify,
    ):
        process_s3_raw_documents(input_file, output_folder, silent)

        mock_notify.assert_not_called()
