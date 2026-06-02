from src.parsers import get_file_parser
from src.parsers.telegram import TelegramParser
from src.parsers.tiktok import TikTokParser
from src.parsers.twitter import TwitterParser


class TestGetFileParser:
    def test_get_telegram_parser(self):
        input_file = "telegram/topic_id/posts.jsonl"
        assert isinstance(get_file_parser(input_file), TelegramParser)

    def test_get_twitter_parser(self):
        input_file = "twitter/topic_id/posts.jsonl"
        assert isinstance(get_file_parser(input_file), TwitterParser)

    def test_get_tiktok_parser(self):
        input_file = "tiktok/topic_id/posts.jsonl"
        assert isinstance(get_file_parser(input_file), TikTokParser)
