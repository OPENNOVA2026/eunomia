import re
from abc import ABC, abstractmethod

from src.models.shared import Interaction, Post, Source
from src.utils import extract_uuid


class BaseParser(ABC):
    source: Source

    def __init__(self, input_file: str):
        self.topic_id = extract_uuid(input_file, "topic")
        self.research_id = extract_uuid(input_file, "research")

    @abstractmethod
    def normalize_raw_document(self, document: dict) -> Post:
        raise NotImplementedError

    @abstractmethod
    def get_document_interactions(self, document: dict) -> list[Interaction]:
        raise NotImplementedError

    def clean_text(self, full_text: str | None) -> str | None:
        if full_text is None:
            return None

        text = full_text

        text = self.__remove_rt_prefix(text)
        text = self.__remove_urls(text)
        text = self.__remove_mentions(text)
        text = self.__remove_unicodes(text)
        text = self.__remove_emojis(text)
        text = self.__normalize_white_spaces(text)

        return text.lower()

    def __remove_rt_prefix(self, text: str) -> str:
        return re.sub(r"^RT\s+(@\w+:\s*)?", "", text, flags=re.IGNORECASE)

    def __remove_urls(self, text: str) -> str:
        url_pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            re.UNICODE,
        )
        return re.sub(url_pattern, "", text)

    def __remove_mentions(self, text: str) -> str:
        return re.sub(r"@\w+", "", text)

    def __remove_unicodes(self, text: str) -> str:
        """Removes unicode strings like '\\u002c' and decodes '&amp;'."""
        text = re.sub(r"(\\u[0-9A-Fa-f]+)", "", text)
        text = re.sub(r"&amp;", "&", text)
        return text.strip()

    def __remove_emojis(self, text: str) -> str:
        emoji_pattern = re.compile(
            "[\U0001f600-\U0001f64f"  # Emoticons
            "\U0001f300-\U0001f5ff"  # Miscellaneous symbols and pictographs
            "\U0001f680-\U0001f6ff"  # Transport and map symbols
            "\U0001f700-\U0001f77f"  # Alchemical symbols
            "\U0001f780-\U0001f7ff"  # Geometric shapes
            "\U0001f800-\U0001f8ff"  # Supplemental arrows-C
            "\U0001f900-\U0001f9ff"  # Supplemental symbols and pictographs
            "\U0001fa00-\U0001fa6f"  # Chess symbols
            "\U0001fa70-\U0001faff"  # Symbols for various other purposes
            "\U00002702-\U000027b0"  # Dingbats
            "\U000024c2-\U0001f251"  # Enclosed characters
            "]+",
            flags=re.UNICODE,
        )

        return re.sub(emoji_pattern, "", text)

    def __normalize_white_spaces(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
