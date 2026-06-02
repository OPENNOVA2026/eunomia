from unittest.mock import patch

import pytest

from src.clients.external import notify_raw_documents_analyzed


class TestNotifyRawDocumentsAnalyzed:
    """Tests for the notify_raw_documents_analyzed function"""

    @patch("src.clients.external.__post")
    def test_notify_with_minimal_parameters(self, mock_post):
        """Test notification with only required parameters"""
        # Execute
        notify_raw_documents_analyzed(input_file="input.pdf")

        # Assert
        mock_post.assert_called_once_with(
            {"input_file": "input.pdf", "status": "ok"},
        )

    @patch("src.clients.external.__post")
    def test_notify_with_custom_status(self, mock_post):
        """Test notification with custom status"""
        # Execute
        notify_raw_documents_analyzed(input_file="input.pdf", status="error")

        # Assert
        mock_post.assert_called_once_with(
            {"input_file": "input.pdf", "status": "error"},
        )

    @patch("src.clients.external.__post")
    def test_notify_with_files(self, mock_post):
        """Test notification with files list"""
        # Execute
        files = ["file1.pdf", "file2.pdf"]
        notify_raw_documents_analyzed(input_file="input.pdf", files=files)

        # Assert
        mock_post.assert_called_once_with(
            {
                "input_file": "input.pdf",
                "status": "ok",
                "files": ["file1.pdf", "file2.pdf"],
            },
        )

    @patch("src.clients.external.__post")
    def test_notify_with_detail(self, mock_post):
        """Test notification with detail message"""
        # Execute
        notify_raw_documents_analyzed(
            input_file="input.pdf", detail="Processing completed successfully"
        )

        # Assert
        mock_post.assert_called_once_with(
            {
                "input_file": "input.pdf",
                "status": "ok",
                "detail": "Processing completed successfully",
            },
        )

    @patch("src.clients.external.__post")
    def test_notify_with_all_parameters(self, mock_post):
        """Test notification with all parameters"""
        # Execute
        notify_raw_documents_analyzed(
            input_file="input.pdf",
            status="error",
            files=["output1.json", "output2.json"],
            detail="Processing failed due to timeout",
        )

        # Assert
        mock_post.assert_called_once_with(
            {
                "input_file": "input.pdf",
                "status": "error",
                "files": ["output1.json", "output2.json"],
                "detail": "Processing failed due to timeout",
            },
        )

    @patch("src.clients.external.__post")
    def test_notify_with_empty_files_list(self, mock_post):
        """Test notification with empty files list (should not include files key)"""
        # Execute
        notify_raw_documents_analyzed(input_file="input.pdf", files=[])

        # Assert
        mock_post.assert_called_once_with(
            {"input_file": "input.pdf", "status": "ok"},
        )

    @patch("src.clients.external.__post")
    def test_notify_with_none_detail(self, mock_post):
        """Test notification with None detail (should not include detail key)"""
        # Execute
        notify_raw_documents_analyzed(input_file="input.pdf", detail=None)

        # Assert
        mock_post.assert_called_once_with(
            {"input_file": "input.pdf", "status": "ok"},
        )

    @patch("src.clients.external.__post")
    def test_notify_propagates_post_exception(self, mock_post):
        """Test that exceptions from __post are propagated"""
        # Setup
        mock_post.side_effect = Exception("Service error")

        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            notify_raw_documents_analyzed(input_file="input.pdf")

        assert "Service error" in str(exc_info.value)
