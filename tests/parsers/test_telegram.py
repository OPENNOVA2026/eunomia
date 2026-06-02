from datetime import datetime, timezone

import pytest

from src.models.shared import Post, Source
from src.parsers.telegram import TelegramParser

parser = TelegramParser("telegram/2025/7/1/documents.jsonl")


@pytest.fixture
def base_document():
    return {
        "id": 12345,
        "date": "2024-07-01T12:34:56Z",
        "message": "Hello, Telegram!",
        "from_id": {"user_id": 98765},
        "post_author": "user123",
        "peer_id": {"channel_id": 11111},
        "replies": [{"id": 1}, {"id": 2}],
        "reactions": {
            "results": [
                {"reaction": "like", "count": 3},
                {"reaction": "love", "count": 2},
            ]
        },
        "meta": {"channel_name": "canal_123"},
    }


def test_normalize_raw_document_all_fields(base_document):
    post = parser.normalize_raw_document(base_document)

    assert isinstance(post, Post)
    assert post.primitive_id == "12345"
    assert post.full_text == "Hello, Telegram!"
    assert post.cleaned_text == parser.clean_text("Hello, Telegram!")
    assert post.created_at == datetime(2024, 7, 1, 12, 34, 56, tzinfo=timezone.utc)
    assert post.author_id == "98765"
    assert post.author_username == "user123"
    assert post.channel_id == "11111"
    assert post.n_replies == 2
    assert post.n_likes == 5
    assert post.source == Source.TELEGRAM
    assert post.channel_name == "canal_123"


def test_normalize_raw_document_missing_optional_fields(base_document):
    base_document.pop("from_id")
    base_document.pop("replies")
    base_document.pop("reactions")
    base_document.pop("meta")

    post = parser.normalize_raw_document(base_document)

    assert post.author_id is None
    assert post.n_replies is None
    assert post.n_likes is None
    assert post.channel_name is None


def test_get_document_interactions_returns_empty_list(base_document):
    interactions = parser.get_document_interactions(base_document)
    assert isinstance(interactions, list)
    assert interactions == []
