from unittest.mock import patch

import pytest

from src.models.shared import Interaction, InteractionType, Post, Source
from src.parsers.twitter import TwitterParser


class TestTwitterParser:
    TOPIC_ID = "743de01b-2cbf-4858-b6f4-8cf19f202287"

    @pytest.fixture
    def parser(self):
        input_file = f"topic_{self.TOPIC_ID}/2026/1/1/documents.jsonl"
        parser = TwitterParser(input_file)
        return parser

    @pytest.fixture
    def sample_document(self):
        return {
            "id": "1234567890",
            "created_at": "2024-01-15T10:30:45.123Z",
            "text": "This is a test tweet #testing @user1",
            "author_id": "987654321",
            "user": {"username": "testuser"},
            "public_metrics": {
                "retweet_count": 10,
                "quote_count": 5,
                "reply_count": 3,
                "like_count": 25,
                "impression_count": 1000,
            },
            "entities": {
                "hashtags": [{"tag": "testing"}],
                "mentions": [{"username": "user1"}],
            },
            "meta": {"channel_name": "canal_123"},
        }

    @pytest.fixture
    def document_with_retweet(self, sample_document):
        doc = sample_document.copy()
        doc["referenced_tweets"] = [
            {
                "type": "retweeted",
                "id": "original_tweet_id",
                "author_id": "original_author_id",
                "user": {"username": "original_user"},
            }
        ]
        return doc

    def test_source_attribute(self, parser: TwitterParser):
        assert parser.source == Source.TWITTER

    def test_base_url_attribute(self, parser: TwitterParser):
        """Test that base_url is set correctly"""
        assert parser.base_url == "https://x.com"

    @patch.object(TwitterParser, "clean_text")
    def test_normalize_raw_document_basic(
        self, mock_clean_text, parser, sample_document
    ):
        """Test basic document normalization"""
        mock_clean_text.return_value = "cleaned text"

        result = parser.normalize_raw_document(sample_document)

        assert isinstance(result, Post)
        assert str(result.topic_id) == self.TOPIC_ID
        assert result.created_at.isoformat() == "2024-01-15T10:30:45.123000+00:00"
        assert result.source == Source.TWITTER
        assert result.primitive_id == "1234567890"
        assert result.author_id == "987654321"
        assert result.author_username == "testuser"
        assert result.full_text == "This is a test tweet #testing @user1"
        assert result.cleaned_text == "cleaned text"
        assert result.is_original is True
        assert result.external_url == "https://x.com/testuser/status/1234567890"
        assert result.hashtags == ["testing"]
        assert result.mentions == ["user1"]
        assert result.n_reposts == 10
        assert result.n_quotes == 5
        assert result.n_replies == 3
        assert result.n_likes == 25
        assert result.n_impressions == 1000
        assert result.channel_name is None

        mock_clean_text.assert_called_once_with("This is a test tweet #testing @user1")

    @patch.object(TwitterParser, "clean_text")
    def test_normalize_raw_document_retweet(
        self, mock_clean_text, parser, document_with_retweet
    ):
        """Test document normalization for retweets"""
        mock_clean_text.return_value = "cleaned text"

        result = parser.normalize_raw_document(document_with_retweet)

        assert result.is_original is False

    @patch.object(TwitterParser, "clean_text")
    def test_normalize_raw_document_no_entities(
        self, mock_clean_text, parser, sample_document
    ):
        """Test document normalization when entities are missing"""
        mock_clean_text.return_value = "cleaned text"
        del sample_document["entities"]

        result = parser.normalize_raw_document(sample_document)

        assert result.hashtags == []
        assert result.mentions == []

    @patch.object(TwitterParser, "clean_text")
    def test_normalize_raw_document_partial_entities(
        self, mock_clean_text, parser, sample_document
    ):
        """Test document normalization with partial entities"""
        mock_clean_text.return_value = "cleaned text"
        sample_document["entities"] = {"hashtags": [{"tag": "test"}]}  # No mentions

        result = parser.normalize_raw_document(sample_document)

        assert result.hashtags == ["test"]
        assert result.mentions == []

    @patch.object(TwitterParser, "clean_text")
    def test_normalize_raw_document_missing_metrics(
        self, mock_clean_text, parser, sample_document
    ):
        """Test document normalization with missing public metrics"""
        mock_clean_text.return_value = "cleaned text"
        sample_document["public_metrics"] = {
            "retweet_count": 5
        }  # Missing other metrics

        result = parser.normalize_raw_document(sample_document)

        assert result.n_reposts == 5
        assert result.n_quotes is None
        assert result.n_replies is None
        assert result.n_likes is None
        assert result.n_impressions is None

    def test_normalize_raw_document_invalid_date_format(self, parser, sample_document):
        """Test that invalid date format raises appropriate error"""
        sample_document["created_at"] = "invalid-date-format"

        with pytest.raises(ValueError):
            parser.normalize_raw_document(sample_document)

    def test_get_document_interactions_no_references(self, parser, sample_document):
        """Test get_document_interactions with no referenced tweets"""
        result = parser.get_document_interactions(sample_document)

        assert result == []

    def test_get_document_interactions_with_references(self, parser, sample_document):
        """Test get_document_interactions with referenced tweets"""
        sample_document["referenced_tweets"] = [
            {
                "type": "replied_to",
                "id": "ref_tweet_1",
                "author_id": "ref_author_1",
                "author": {"id": "ref_author_1", "username": "ref_user_1"},
            },
            {
                "type": "retweeted",
                "id": "ref_tweet_2",
                "author_id": "ref_author_2",
                "author": {"id": "ref_author_2", "username": "ref_user_2"},
            },
        ]

        result = parser.get_document_interactions(sample_document)

        assert len(result) == 2

        # Test first interaction (reply)
        interaction1 = result[0]
        assert isinstance(interaction1, Interaction)
        assert str(interaction1.topic_id) == self.TOPIC_ID
        assert interaction1.created_at.isoformat() == "2024-01-15T10:30:45.123000+00:00"
        assert interaction1.interaction_type == InteractionType.REPLY
        assert interaction1.source_author_id == "987654321"
        assert interaction1.source_author_username == "testuser"
        assert interaction1.source_model_id == "1234567890"
        assert interaction1.target_author_id == "ref_author_1"
        assert interaction1.target_author_username == "ref_user_1"
        assert interaction1.target_model_id == "ref_tweet_1"
        assert interaction1.model_type == "post"
        assert interaction1.n_likes is None

        # Test second interaction (retweet)
        interaction2 = result[1]
        assert isinstance(interaction2, Interaction)
        assert interaction2.interaction_type == InteractionType.REPOST
        assert interaction1.source_author_id == "987654321"
        assert interaction1.source_author_username == "testuser"
        assert interaction1.source_model_id == "1234567890"
        assert interaction2.target_author_id == "ref_author_2"
        assert interaction2.target_author_username == "ref_user_2"
        assert interaction2.target_model_id == "ref_tweet_2"
        assert interaction1.model_type == "post"
        assert interaction2.n_likes is None

    def test_get_document_interactions_incomplete_reference(
        self, parser, sample_document
    ):
        """Test get_document_interactions with incomplete reference data"""
        sample_document["referenced_tweets"] = [
            {
                "type": "replied_to",
                "id": "ref_tweet_1",
                # Missing author_id and user
            },
            {
                "type": "retweeted",
                "id": "ref_tweet_2",
                "author_id": "ref_author_2",
                "author": {"id": "ref_author_2", "username": "ref_user_2"},
            },
        ]

        result = parser.get_document_interactions(sample_document)

        # Should only return the complete interaction
        assert len(result) == 1
        assert result[0].interaction_type == InteractionType.REPOST
        assert result[0].n_likes is None

    def test_map_interaction_type_reply(self, parser):
        """Test interaction type mapping for replies"""
        result = parser._TwitterParser__map_interaction_type("replied_to")
        assert result == InteractionType.REPLY

    def test_map_interaction_type_retweet(self, parser):
        """Test interaction type mapping for retweets"""
        result = parser._TwitterParser__map_interaction_type("retweeted")
        assert result == InteractionType.REPOST

    def test_map_interaction_type_quote(self, parser):
        """Test interaction type mapping for quotes"""
        result = parser._TwitterParser__map_interaction_type("quoted")
        assert result == InteractionType.QUOTE

    def test_map_interaction_type_invalid(self, parser):
        """Test that invalid interaction type raises KeyError"""
        with pytest.raises(KeyError):
            parser._TwitterParser__map_interaction_type("invalid_type")

    @patch.object(TwitterParser, "clean_text")
    def test_normalize_raw_document_none_values(self, mock_clean_text, parser):
        """Test document normalization with minimal required fields"""
        mock_clean_text.return_value = "cleaned text"

        minimal_document = {
            "id": "123",
            "created_at": "2024-01-15T10:30:45.123Z",
            "text": "minimal tweet",
            "author_id": "456",
            "user": {"username": "minimal_user"},
            "public_metrics": {},
        }

        result = parser.normalize_raw_document(minimal_document)

        assert result.primitive_id == "123"
        assert result.author_id == "456"
        assert result.author_username == "minimal_user"
        assert result.full_text == "minimal tweet"
        assert result.hashtags == []
        assert result.mentions == []
        assert result.n_reposts is None
        assert result.n_quotes is None
        assert result.n_replies is None
        assert result.n_likes is None
        assert result.n_impressions is None

    def test_inheritance_from_base_parser(self, parser):
        """Test that TwitterParser inherits from BaseParser"""
        from src.parsers.base import BaseParser

        assert isinstance(parser, BaseParser)

    @pytest.mark.parametrize(
        "ref_type,expected_original",
        [
            ([], True),  # No references
            ([{"type": "replied_to"}], True),  # Reply only
            ([{"type": "quoted"}], True),  # Quote only
            ([{"type": "retweeted"}], False),  # Retweet
            (
                [{"type": "replied_to"}, {"type": "quoted"}],
                True,
            ),  # Multiple non-retweets
            (
                [{"type": "replied_to"}, {"type": "retweeted"}],
                False,
            ),  # Mixed with retweet
        ],
    )
    @patch.object(TwitterParser, "clean_text")
    def test_is_original_logic(
        self, mock_clean_text, parser, sample_document, ref_type, expected_original
    ):
        """Test is_original logic with various reference combinations"""
        mock_clean_text.return_value = "cleaned text"
        sample_document["referenced_tweets"] = ref_type

        result = parser.normalize_raw_document(sample_document)

        assert result.is_original == expected_original
