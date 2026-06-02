from datetime import datetime, timezone

from src.models.shared import Interaction, Post, Source
from src.parsers.base import BaseParser


class TelegramParser(BaseParser):
    source = Source.TELEGRAM

    def normalize_raw_document(self, document: dict) -> Post:
        date = datetime.strptime(document["date"], "%Y-%m-%dT%H:%M:%S%z")
        created_at = date.replace(tzinfo=timezone.utc)

        from_id: dict = document.get("from_id")

        replies = document.get("replies")
        n_likes = None
        if reactions := document.get("reactions"):
            n_likes = sum(result["count"] for result in reactions["results"])

        return Post(
            topic_id=None,
            source=self.source,
            research_id=None,
            is_truthful=None,
            #
            created_at=created_at,
            primitive_id=str(document["id"]),
            full_text=document["message"],
            cleaned_text=self.clean_text(document["message"]),
            is_original=True,
            #
            full_transcription=None,
            cleaned_transcription=None,
            #
            author_id=str(from_id.get("user_id")) if from_id else None,
            author_username=document.get("post_author"),
            channel_id=str(document["peer_id"]["channel_id"]),
            channel_name=document.get("meta", {}).get("channel_name", None),
            external_url=None,
            hashtags=None,
            mentions=None,
            #
            n_reposts=None,
            n_quotes=None,
            n_replies=len(replies) if replies is not None else None,
            n_likes=n_likes,
            n_impressions=None,
            n_saves=None,
            #
            meta=None,
        )

    def get_document_interactions(self, document: dict) -> list[Interaction]:
        return []
