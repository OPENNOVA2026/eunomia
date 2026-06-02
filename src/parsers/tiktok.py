from datetime import datetime, timezone

from src.models.shared import Interaction, InteractionType, Post, Source
from src.parsers.base import BaseParser


class TikTokParser(BaseParser):
    source = Source.TIKTOK

    def normalize_raw_document(self, document):
        date = datetime.strptime(document["createTimeISO"], "%Y-%m-%dT%H:%M:%S.%fZ")
        created_at = date.replace(tzinfo=timezone.utc)

        author_meta: dict = document.get("authorMeta")
        hashtags_meta: list[dict] = document.get("hashtags")
        mentions = [m.lstrip("@") for m in document["mentions"]]

        return Post(
            topic_id=self.topic_id,
            source=self.source,
            research_id=None,
            is_truthful=None,
            #
            created_at=created_at,
            primitive_id=document["id"],
            full_text=document["text"],
            cleaned_text=self.clean_text(document["text"]),
            is_original=True,
            #
            full_transcription=document["transcription"],
            cleaned_transcription=self.clean_text(document["transcription"]),
            #
            author_id=author_meta.get("id"),
            author_username=author_meta.get("name"),
            channel_id=None,
            channel_name=None,
            external_url=document.get("webVideoUrl"),
            hashtags=[h.get("name") for h in hashtags_meta if h.get("name")] or None,
            mentions=mentions,
            #
            n_reposts=document["shareCount"],
            n_quotes=None,
            n_replies=None,
            n_likes=document["diggCount"],
            n_impressions=document["playCount"],
            n_saves=document["collectCount"],
            #
            meta=None,
        )

    def get_document_interactions(self, document):
        author_meta: dict = document.get("authorMeta")
        interactions: list[Interaction] = []
        comments: list[dict] = document.get("comments", [])
        for comment in comments:
            if comment["text"].strip() == "":
                continue
            if not comment.get("uniqueId"):
                continue
            date = datetime.strptime(comment["createTimeISO"], "%Y-%m-%dT%H:%M:%S.%fZ")
            created_at = date.replace(tzinfo=timezone.utc)
            interactions.append(
                Interaction(
                    topic_id=self.topic_id,
                    source=self.source,
                    #
                    created_at=created_at,
                    interaction_type=InteractionType.COMMENT,
                    model_type="post",
                    source_author_id=comment["uid"],
                    source_author_username=comment["uniqueId"],
                    source_model_id=comment["cid"],
                    target_author_id=author_meta.get("id"),
                    target_author_username=author_meta.get("name"),
                    target_model_id=document["id"],
                    #
                    n_likes=comment.get("diggCount", 0),
                    #
                    full_text=comment["text"],
                    cleaned_text=self.clean_text(comment["text"]),
                )
            )
        return interactions
