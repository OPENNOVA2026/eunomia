from src.models.shared import Source
from src.parsers.base import BaseParser
from src.parsers.telegram import TelegramParser
from src.parsers.tiktok import TikTokParser
from src.parsers.twitter import TwitterParser
from src.parsers.twitter_apify import TwitterApifyParser

PARSERS = {
    Source.TELEGRAM: TelegramParser,
    Source.TWITTER: TwitterParser,
    Source.TWITTER_APIFY: TwitterApifyParser,
    Source.TIKTOK: TikTokParser,
}


def get_file_parser(input_file: str) -> BaseParser:
    source = input_file.split("/")[0]
    return PARSERS[source](input_file)
