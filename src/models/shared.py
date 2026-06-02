"""
⚠️ WARNING: DO NOT MODIFY THIS FILE UNLESS STRICTLY NECESSARY ⚠️

This file contains all normalized data models used across the system. Before making any
changes, please consult the documentation and check the latest model definitions at:

👉 https://www.notion.so/Normalizaci-n-de-datos-201ecffec00680199b29c332eb0a7699

Any modifications may affect multiple parts of the system. Proceed with caution and
coordinate with the team if changes are required.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class Source(str, Enum):
    TELEGRAM = "telegram"
    TWITTER = "twitter"
    TWITTER_APIFY = "twitter_apify"
    TIKTOK = "tiktok"


class Post(BaseModel):
    topic_id: UUID | None
    source: Source  # "twitter" || "bluesky"
    research_id: None = None
    is_truthful: bool | None

    created_at: datetime
    primitive_id: str  # El ID del post propio de la red social
    full_text: str  # Texto sin modificar
    cleaned_text: str  # Texto limpio de emojis, links, etc.
    is_original: bool  # Si el texto contiene información original del autor

    full_transcription: str | None  # Transcripción de vídeos
    cleaned_transcription: str | None

    author_id: str | None  # El "primitive_id" del autor
    author_username: str | None  # !OJO
    channel_id: str | None  # El "primitive_id" del canal de envío
    channel_name: str | None
    external_url: str | None  # Enlace al post original
    hashtags: list[str] | None  # null || [] || ["europapress"]
    mentions: list[str] | None  # Los "primitive_id" de los autores mencionados

    n_reposts: int | None
    n_quotes: int | None
    n_replies: int | None
    n_likes: int | None
    n_impressions: int | None
    n_saves: int | None

    meta: dict | None  # Any custom info. IDEALLY ALWAYS NULL


class InteractionType(str, Enum):
    FOLLOW = "follow"
    MENTION = "mention"
    REPOST = "repost"
    QUOTE = "quote"
    REPLY = "reply"
    COMMENT = "comment"


class InteractionModelType(str, Enum):
    POST = Post.__name__.lower()


class Interaction(BaseModel):
    topic_id: UUID | None
    source: Source

    created_at: datetime
    interaction_type: (
        InteractionType  # "follow" || "mention" || "repost" || "quote" || "reply"
    )
    model_type: InteractionModelType  # "post" || "comment" || ...
    source_author_id: str  # El "primitive_id" autor que inicia la interacción
    source_author_username: str  # !OJO
    source_model_id: str  # El "primitive_id" del modelo que inicia la interacción
    target_author_id: str  # El "primitive_id" autor objetivo de la interacción
    target_author_username: str
    target_model_id: str  # El "primitive_id" del modelo objetivo de la interacción
    #
    n_likes: int | None
    #
    full_text: str | None  # texto en comentarios
    cleaned_text: str | None
