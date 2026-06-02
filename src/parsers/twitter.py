from datetime import datetime, timezone

from src.models.shared import Interaction, InteractionType, Post, Source
from src.parsers.base import BaseParser


class TwitterParser(BaseParser):
    source = Source.TWITTER
    base_url = "https://x.com"

    def normalize_raw_document(self, document: dict) -> Post:
        created_at = datetime.strptime(document["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        created_at_utc = created_at.replace(tzinfo=timezone.utc)
        primitive_id = document["id"]
        username = document["user"]["username"]
        external_url = f"{self.base_url}/{username}/status/{primitive_id}"
        ref_tweets = document.get("referenced_tweets", [])
        is_original = next(
            (False for ref_tweet in ref_tweets if ref_tweet["type"] == "retweeted"),
            True,
        )

        entities: dict = document.get("entities", {})
        hashtags: list = entities.get("hashtags", [])
        mentions: list = entities.get("mentions", [])

        public_metrics: dict = document["public_metrics"]

        return Post(
            topic_id=self.topic_id,
            source=self.source,
            research_id=self.research_id,
            is_truthful=None,
            #
            created_at=created_at_utc,
            primitive_id=primitive_id,
            full_text=document["text"],
            cleaned_text=self.clean_text(document["text"]),
            is_original=is_original,
            #
            full_transcription=None,
            cleaned_transcription=None,
            #
            author_id=str(document["author_id"]),
            author_username=username,
            channel_id=None,
            channel_name=None,
            external_url=external_url,
            hashtags=[h["tag"] for h in hashtags],
            mentions=[m["username"] for m in mentions],
            #
            n_reposts=public_metrics.get("retweet_count"),
            n_quotes=public_metrics.get("quote_count"),
            n_replies=public_metrics.get("reply_count"),
            n_likes=public_metrics.get("like_count"),
            n_impressions=public_metrics.get("impression_count"),
            n_saves=public_metrics.get("bookmark_count"),
            #
            meta=None,
        )

    def get_document_interactions(self, document: dict) -> list[Interaction]:
        created_at = datetime.strptime(document["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        created_at_utc = created_at.replace(tzinfo=timezone.utc)
        interactions: list[Interaction] = []
        references: list[dict] = document.get("referenced_tweets", [])
        for ref in references:
            if ref.get("author"):
                interactions.append(
                    Interaction(
                        topic_id=self.topic_id,
                        source=self.source,
                        #
                        created_at=created_at_utc,
                        interaction_type=self.__map_interaction_type(ref["type"]),
                        model_type="post",
                        source_author_id=str(document["author_id"]),
                        source_author_username=document["user"]["username"],
                        source_model_id=document["id"],
                        target_author_id=ref["author"]["id"],
                        target_author_username=ref["author"]["username"],
                        target_model_id=ref["id"],
                        #
                        n_likes=None,
                        #
                        full_text=None,
                        cleaned_text=None,
                    )
                )

        return interactions

    def __map_interaction_type(self, type: str) -> InteractionType:
        return {
            "replied_to": InteractionType.REPLY,
            "retweeted": InteractionType.REPOST,
            "quoted": InteractionType.QUOTE,
        }[type]
