import contextlib
from datetime import datetime, timezone

from src.models.shared import Interaction, InteractionType, Post, Source
from src.parsers.base import BaseParser


class TwitterApifyParser(BaseParser):
    source = Source.TWITTER
    base_url = "https://x.com"

    def normalize_raw_document(self, document: dict) -> Post:
        created_at = datetime.strptime(document["createdAt"], "%a %b %d %H:%M:%S %z %Y")
        created_at_utc = created_at.replace(tzinfo=timezone.utc)
        author = document["author"]
        if "id" not in author:
            return

        primitive_id = document["id"]
        external_url = document["url"]
        is_original = not bool(document["isRetweet"])

        entities: dict = document.get("entities", {})
        hashtags: list = entities.get("hashtags", [])
        mentions: list = entities.get("user_mentions", [])

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
            author_id=str(author["id"]),
            author_username=author.get("userName", author["id"]),
            channel_id=None,
            channel_name=None,
            external_url=external_url,
            hashtags=[h["text"] for h in hashtags],
            mentions=[m["screen_name"] for m in mentions],
            #
            n_reposts=document.get("retweetCount"),
            n_quotes=document.get("quoteCount"),
            n_replies=document.get("replyCount"),
            n_likes=document.get("likeCount"),
            n_impressions=document.get("viewCount"),
            n_saves=document.get("bookmarkCount"),
            #
            meta=None,
        )

    def get_document_interactions(self, document: dict) -> list[Interaction]:
        created_at = datetime.strptime(document["createdAt"], "%a %b %d %H:%M:%S %z %Y")
        created_at_utc = created_at.replace(tzinfo=timezone.utc)
        interactions: list[Interaction] = []

        if retweet := document.get("retweet"):
            author = document["author"]
            if "id" not in author:
                return []

            author_id = str(document["author"]["id"])
            # Get first mention as a backup
            user_mentions = document.get("entities", {}).get("user_mentions", [])
            with contextlib.suppress(IndexError):
                first_mention = user_mentions[0]

            with contextlib.suppress(UnboundLocalError):
                interactions.append(
                    Interaction(
                        topic_id=self.topic_id,
                        source=self.source,
                        #
                        created_at=created_at_utc,
                        interaction_type=InteractionType.REPOST,
                        model_type="post",
                        source_author_id=author_id,
                        source_author_username=author.get("userName", author_id),
                        source_model_id=document["id"],
                        target_author_id=retweet["author"].get(
                            "id", first_mention["id_str"]
                        ),
                        target_author_username=retweet["author"].get(
                            "userName", first_mention["screen_name"]
                        ),
                        target_model_id=retweet["id"],
                        #
                        n_likes=None,
                        #
                        full_text=None,
                        cleaned_text=None,
                    )
                )

        # TODO: Add more interactions if we know more
        return interactions
