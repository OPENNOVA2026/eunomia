from abc import ABC
from unittest.mock import Mock

import pytest

from src.models.shared import Interaction, Post, Source
from src.parsers.base import BaseParser


class ConcreteParser(BaseParser):
    """Concrete implementation of BaseParser for testing"""

    source = Source.TWITTER  # Using a valid source for testing

    def normalize_raw_document(self, document: dict) -> Post:
        """Concrete implementation for testing"""
        return Mock(spec=Post)

    def get_document_interactions(self, document: dict) -> list[Interaction]:
        """Concrete implementation for testing"""
        return [Mock(spec=Interaction)]


class TestBaseParser:
    TOPIC_ID = "743de01b-2cbf-4858-b6f4-8cf19f202287"
    RESEARCH_ID = "3b785753-8252-4739-b19e-815a0629d397"

    @pytest.fixture
    def parser(self):
        """Create a concrete parser instance for testing"""
        input_file = (
            f"topic_{self.TOPIC_ID}/research_{self.RESEARCH_ID}/documents.jsonl"
        )
        return ConcreteParser(input_file)

    def test_initialization(self, parser):
        """Test that BaseParser initializes correctly"""
        assert parser.topic_id == self.TOPIC_ID
        assert parser.research_id == self.RESEARCH_ID
        assert parser.source == Source.TWITTER

    def test_is_abstract_base_class(self):
        """Test that BaseParser is an abstract base class"""
        assert issubclass(BaseParser, ABC)

    def test_cannot_instantiate_base_parser_directly(self):
        """Test that BaseParser cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseParser("test_topic")

    def test_abstract_methods_exist(self):
        """Test that abstract methods are defined"""
        abstract_methods = BaseParser.__abstractmethods__
        assert "normalize_raw_document" in abstract_methods
        assert "get_document_interactions" in abstract_methods

    def test_concrete_implementation_works(self, parser):
        """Test that concrete implementation can be instantiated and used"""
        # Test abstract methods are implemented
        result_post = parser.normalize_raw_document({})
        result_interactions = parser.get_document_interactions({})

        assert result_post is not None
        assert isinstance(result_interactions, list)

    def test_clean_text_basic(self, parser):
        """Test basic text cleaning functionality"""
        text = "Hello World!"
        result = parser.clean_text(text)
        assert result == "hello world!"

    def test_clean_text_removes_urls(self, parser):
        """Test URL removal from text"""
        test_cases = [
            ("Check this out https://example.com", "check this out"),
            ("Visit http://test.org for more info", "visit for more info"),
            (
                "Multiple https://site1.com and http://site2.net links",
                "multiple and links",
            ),
            ("https://sub.domain.com/path?param=value", ""),
            (
                "Text with https://example.com/path/to/resource.html more text",
                "text with more text",
            ),
        ]

        for input_text, expected in test_cases:
            result = parser.clean_text(input_text)
            assert result == expected

    def test_clean_text_removes_unicodes(self, parser):
        """Test unicode string removal"""
        test_cases = [
            ("Text with \\u002c unicode", "text with unicode"),
            (
                "Multiple \\u0020\\u0021 unicodes",
                "multiple unicodes",
            ),
            ("\\u0048\\u0065\\u006c\\u006c\\u006f", ""),
            ("Normal text", "normal text"),
        ]

        for input_text, expected in test_cases:
            result = parser.clean_text(input_text)
            assert result == expected

    def test_clean_text_removes_whitespace_chars(self, parser):
        """Test removal of tabs, carriage returns, and newlines"""
        test_cases = [
            ("Text\twith\ttabs", "text with tabs"),
            ("Text\nwith\nnewlines", "text with newlines"),
            ("Text\rwith\rcarriage", "text with carriage"),
            ("Mixed\t\n\rwhitespace", "mixed whitespace"),
            ("\t\n\rOnly whitespace\t\n\r", "only whitespace"),
        ]

        for input_text, expected in test_cases:
            result = parser.clean_text(input_text)
            assert result == expected

    def test_clean_text_handles_html_entities(self, parser):
        """Test HTML entity replacement"""
        test_cases = [
            ("Text &amp; more text", "text & more text"),
            ("Multiple &amp; entities &amp; here", "multiple & entities & here"),
            ("Only &amp;", "only &"),
            ("No entities", "no entities"),
        ]

        for input_text, expected in test_cases:
            result = parser.clean_text(input_text)
            assert result == expected

    def test_clean_text_removes_emojis(self, parser):
        """Test emoji removal from text"""
        test_cases = [
            ("Hello 😀 World!", "hello world!"),
            ("Multiple 🚀🎉✨ emojis", "multiple emojis"),
            ("Text with 🌟 emoji 🎯 in middle", "text with emoji in middle"),
            ("🔥🔥🔥", ""),
            ("No emojis here", "no emojis here"),
            (
                "Mixed content 😊 with URL https://example.com",
                "mixed content with url",
            ),
        ]

        for input_text, expected in test_cases:
            result = parser.clean_text(input_text)
            assert result == expected

    def test_clean_text_comprehensive(self, parser):
        """Test comprehensive text cleaning with all features"""
        complex_text = """
        Check out this cool site: https://example.com 🚀
        It has lots of info!\t\n
        Unicode test: \\u0048\\u0065\\u006c\\u006c\\u006f
        HTML entities: Tom &amp; Jerry
        More emojis: 🎉✨🌟
        """

        result = parser.clean_text(complex_text)

        # Should not contain URLs
        assert "https://example.com" not in result
        # Should not contain emojis
        assert "🚀" not in result and "🎉" not in result
        # Should not contain unicode strings
        assert "\\u0048" not in result
        # Should have HTML entities converted
        assert "&" in result and "&amp;" not in result
        # Should be lowercase
        assert result.islower()
        # Should not contain tabs/newlines
        assert "\t" not in result and "\n" not in result

    def test_clean_text_empty_and_whitespace(self, parser):
        """Test cleaning of empty and whitespace-only strings"""
        test_cases = [
            ("", ""),
            ("   ", ""),
            ("\t\n\r", ""),
            ("   \t  \n  \r  ", ""),
        ]

        for input_text, expected in test_cases:
            result = parser.clean_text(input_text)
            assert result == expected

    def test_clean_text_preserves_normal_punctuation(self, parser):
        """Test that normal punctuation is preserved"""
        text = "Hello, world! How are you? I'm fine."
        result = parser.clean_text(text)
        assert result == "hello, world! how are you? i'm fine."

    def test_clean_text_strips_whitespace(self, parser):
        """Test that leading/trailing whitespace is stripped"""
        test_cases = [
            ("  hello world  ", "hello world"),
            ("\t\nhello world\t\n", "hello world"),
            ("   spaces everywhere   ", "spaces everywhere"),
        ]

        for input_text, expected in test_cases:
            result = parser.clean_text(input_text)
            assert result == expected

    @pytest.mark.parametrize(
        "emoji,description",
        [
            ("😀", "emoticon"),
            ("🚀", "transport symbol"),
            ("🌟", "miscellaneous symbol"),
            ("⚡", "dingbat"),
            ("🔥", "miscellaneous symbol"),
            ("💯", "miscellaneous symbol"),
            ("🎉", "miscellaneous symbol"),
        ],
    )
    def test_clean_text_removes_specific_emojis(self, parser, emoji, description):
        """Test removal of specific emoji categories"""
        text = f"Text with {emoji} emoji"
        result = parser.clean_text(text)
        assert emoji not in result
        assert result == "text with emoji"

    def test_url_regex_patterns(self, parser):
        """Test various URL patterns are caught"""
        url_patterns = [
            "http://example.com",
            "https://example.com",
            "https://www.example.com",
            "https://sub.domain.example.com",
            "https://example.com/path",
            "https://example.com/path?query=value",
            "https://example.com/path?q1=v1&q2=v2",
            "https://example.com:8080/path",
            "http://192.168.1.1:3000/api",
        ]

        for url in url_patterns:
            text = f"Check out {url} for more info"
            result = parser.clean_text(text)
            assert url not in result
            assert result == "check out for more info"

    def test_private_method_access(self, parser):
        """Test that private methods exist (name mangling)"""
        # Private methods should be accessible via name mangling
        assert hasattr(parser, "_BaseParser__remove_urls")
        assert hasattr(parser, "_BaseParser__remove_unicodes")
        assert hasattr(parser, "_BaseParser__remove_emojis")

    def test_source_attribute_requirement(self):
        """Test that concrete classes must define source attribute"""

        class IncompleteParser(BaseParser):
            # Missing source attribute
            def normalize_raw_document(self, document: dict) -> Post:
                return Mock(spec=Post)

            def get_document_interactions(self, document: dict) -> list[Interaction]:
                return []

        # Should be able to instantiate but source won't be defined properly
        parser = IncompleteParser("test")
        # The source attribute should not exist or be None
        assert not hasattr(parser, "source") or parser.source is None
