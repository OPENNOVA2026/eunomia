from copy import deepcopy
from unittest.mock import call, patch

import pytest

from src.models.shared import Interaction, InteractionType, Post, Source
from src.parsers.tiktok import TikTokParser


class TestTikTokParser:
    TOPIC_ID = "743de01b-2cbf-4858-b6f4-8cf19f202287"
    RESEARCH_ID = "3b785753-8252-4739-b19e-815a0629d397"

    @pytest.fixture
    def parser(self):
        input_file = (
            "tiktok/"
            f"topic_{self.TOPIC_ID}/research_{self.RESEARCH_ID}/2026/1/1/documents.jsonl"
        )
        return TikTokParser(input_file)

    @pytest.fixture
    def sample_document(self):
        return {
            "id": "7626397841870671125",
            "text": (
                "Post text for TikTok parser "
                "#impostoderenda #contabilidade @user1 @user2"
            ),
            "createTimeISO": "2026-04-08T14:38:46.000Z",
            "authorMeta": {
                "id": "7582681029719475220",
                "name": "mbcontabilidadejf",
            },
            "webVideoUrl": "https://www.tiktok.com/@mbcontabilidadejf/video/7626397841870671125",
            "transcription": "This is a transcript",
            "diggCount": 15,
            "shareCount": 4,
            "playCount": 626,
            "collectCount": 2,
            "mentions": ["@user1", "@user2"],
            "hashtags": [
                {"id": "1631426357060614", "name": "impostoderenda"},
                {"id": "34545687", "name": "contabilidade"},
            ],
            "comments": [
                {
                    "cid": "7617207423850808086",
                    "createTimeISO": "2026-03-14T20:15:25.000Z",
                    "text": "Great video!",
                    "uid": "7351087195736343584",
                    "uniqueId": "juan73153",
                    "diggCount": 7,
                }
            ],
        }

    def test_source_attribute(self, parser: TikTokParser):
        assert parser.source == Source.TIKTOK

    def test_inheritance_from_base_parser(self, parser):
        from src.parsers.base import BaseParser

        assert isinstance(parser, BaseParser)

    @patch.object(TikTokParser, "clean_text")
    def test_normalize_raw_document_basic(
        self, mock_clean_text, parser, sample_document
    ):
        mock_clean_text.side_effect = ["cleaned post", "cleaned transcript"]

        result = parser.normalize_raw_document(sample_document)

        assert isinstance(result, Post)
        assert str(result.topic_id) == self.TOPIC_ID
        assert result.created_at.isoformat() == "2026-04-08T14:38:46+00:00"
        assert result.source == Source.TIKTOK
        assert result.primitive_id == "7626397841870671125"
        assert result.full_text == (
            "Post text for TikTok parser #impostoderenda #contabilidade @user1 @user2"
        )
        assert result.cleaned_text == "cleaned post"
        assert result.is_original is True
        assert result.full_transcription == "This is a transcript"
        assert result.cleaned_transcription == "cleaned transcript"
        assert result.author_id == "7582681029719475220"
        assert result.author_username == "mbcontabilidadejf"
        assert result.external_url == (
            "https://www.tiktok.com/@mbcontabilidadejf/video/7626397841870671125"
        )
        assert result.hashtags == ["impostoderenda", "contabilidade"]
        assert result.mentions == ["user1", "user2"]
        assert result.n_reposts == 4
        assert result.n_likes == 15
        assert result.n_impressions == 626
        assert result.n_saves == 2
        assert result.n_quotes is None
        assert result.n_replies is None

        assert mock_clean_text.call_count == 2
        mock_clean_text.assert_has_calls(
            [
                call(
                    "Post text for TikTok parser "
                    "#impostoderenda #contabilidade @user1 @user2"
                ),
                call("This is a transcript"),
            ]
        )

    def test_normalize_raw_document_empty_mentions_returns_empty_list(
        self, parser, sample_document
    ):
        document = deepcopy(sample_document)
        document["mentions"] = []

        result = parser.normalize_raw_document(document)

        assert result.mentions == []

    def test_normalize_raw_document_invalid_date_format(self, parser, sample_document):
        document = deepcopy(sample_document)
        document["createTimeISO"] = "invalid-date-format"

        with pytest.raises(ValueError):
            parser.normalize_raw_document(document)

    def test_normalize_raw_document_processes_accents_in_full_text(
        self, parser, sample_document
    ):
        document = deepcopy(sample_document)
        document["text"] = (
            "¡ÁRBOL ÚNICO en ACCIÓN! @user1 Visita https://example.com 😀"
        )

        result = parser.normalize_raw_document(document)

        assert result.full_text == (
            "¡ÁRBOL ÚNICO en ACCIÓN! @user1 Visita https://example.com 😀"
        )
        assert result.cleaned_text == "¡árbol único en acción! visita"

    def test_get_document_interactions_no_comments_returns_empty_list(
        self, parser, sample_document
    ):
        document = deepcopy(sample_document)
        document.pop("comments")

        result = parser.get_document_interactions(document)

        assert result == []

    @patch.object(TikTokParser, "clean_text")
    def test_get_document_interactions_filters_blank_comments(
        self, mock_clean_text, parser, sample_document
    ):
        document = deepcopy(sample_document)
        document["comments"] = [
            {
                "cid": "blank-1",
                "createTimeISO": "2026-03-14T20:15:25.000Z",
                "text": "   ",
                "uid": "u-blank",
                "uniqueId": "blank_user",
            },
            {
                "cid": "7617207423850808086",
                "createTimeISO": "2026-03-14T20:15:25.000Z",
                "text": "Great video!",
                "uid": "7351087195736343584",
                "uniqueId": "juan73153",
            },
        ]
        mock_clean_text.return_value = "great video!"

        result = parser.get_document_interactions(document)

        assert len(result) == 1
        assert result[0].source_model_id == "7617207423850808086"
        assert mock_clean_text.call_count == 1

    @patch.object(TikTokParser, "clean_text")
    def test_get_document_interactions_skips_comment_without_unique_id(
        self, mock_clean_text, parser, sample_document
    ):
        document = deepcopy(sample_document)
        document["comments"] = [
            {
                "cid": "without-unique-id",
                "createTimeISO": "2026-03-14T20:15:25.000Z",
                "text": "This one should be skipped",
                "uid": "user-without-unique-id",
            },
            {
                "cid": "with-unique-id",
                "createTimeISO": "2026-03-14T20:16:25.000Z",
                "text": "This one should be processed",
                "uid": "user-with-unique-id",
                "uniqueId": "valid_user",
            },
        ]
        mock_clean_text.return_value = "this one should be processed"

        result = parser.get_document_interactions(document)

        assert len(result) == 1
        assert {interaction.source_model_id for interaction in result} == {
            "with-unique-id"
        }
        assert result[0].source_model_id == "with-unique-id"
        assert result[0].source_author_username == "valid_user"
        mock_clean_text.assert_called_once_with("This one should be processed")

    @patch.object(TikTokParser, "clean_text")
    def test_get_document_interactions_builds_comment_interaction_correctly(
        self, mock_clean_text, parser, sample_document
    ):
        mock_clean_text.return_value = "great video!"

        result = parser.get_document_interactions(sample_document)

        assert len(result) == 1
        interaction = result[0]
        assert isinstance(interaction, Interaction)
        assert str(interaction.topic_id) == self.TOPIC_ID
        assert interaction.source == Source.TIKTOK
        assert interaction.created_at.isoformat() == "2026-03-14T20:15:25+00:00"
        assert interaction.interaction_type == InteractionType.COMMENT
        assert interaction.model_type == "post"
        assert interaction.source_author_id == "7351087195736343584"
        assert interaction.source_author_username == "juan73153"
        assert interaction.source_model_id == "7617207423850808086"
        assert interaction.target_author_id == "7582681029719475220"
        assert interaction.target_author_username == "mbcontabilidadejf"
        assert interaction.target_model_id == "7626397841870671125"
        assert interaction.n_likes == 7
        assert interaction.full_text == "Great video!"
        assert interaction.cleaned_text == "great video!"

    @patch.object(TikTokParser, "clean_text")
    def test_get_document_interactions_multiple_comments(
        self, mock_clean_text, parser, sample_document
    ):
        document = deepcopy(sample_document)
        document["comments"] = [
            {
                "cid": "comment-1",
                "createTimeISO": "2026-03-14T20:15:25.000Z",
                "text": "First comment",
                "uid": "user-1",
                "uniqueId": "first_user",
            },
            {
                "cid": "comment-2",
                "createTimeISO": "2026-03-14T20:16:25.000Z",
                "text": "Second comment",
                "uid": "user-2",
                "uniqueId": "second_user",
            },
        ]
        mock_clean_text.side_effect = ["first comment", "second comment"]

        result = parser.get_document_interactions(document)

        assert len(result) == 2
        assert result[0].source_model_id == "comment-1"
        assert result[1].source_model_id == "comment-2"
        assert result[0].cleaned_text == "first comment"
        assert result[1].cleaned_text == "second comment"

    def test_get_document_interactions_invalid_comment_date_raises(
        self, parser, sample_document
    ):
        document = deepcopy(sample_document)
        document["comments"] = [
            {
                "cid": "comment-1",
                "createTimeISO": "invalid-date-format",
                "text": "A valid non-empty comment",
                "uid": "user-1",
                "uniqueId": "first_user",
            }
        ]

        with pytest.raises(ValueError):
            parser.get_document_interactions(document)
