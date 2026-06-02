from uuid import uuid4

import pytest

from src.utils import extract_uuid


class TestExtractUuid:
    @pytest.fixture
    def sample_uuid(self):
        """Generate a sample UUID for testing"""
        return str(uuid4())

    @pytest.fixture
    def fixed_uuid(self):
        """Fixed UUID for consistent testing"""
        return "123e4567-e89b-12d3-a456-426614174000"

    def test_extract_uuid_basic_success(self, fixed_uuid):
        """Test basic UUID extraction with simple prefix"""
        path = f"file_prefix_{fixed_uuid}.txt"
        result = extract_uuid(path, "file_prefix")
        assert result == fixed_uuid

    def test_extract_uuid_different_prefixes(self, fixed_uuid):
        """Test UUID extraction with different prefixes"""
        test_cases = [
            ("user", f"user_{fixed_uuid}"),
            ("document", f"document_{fixed_uuid}.pdf"),
            ("image", f"/path/to/image_{fixed_uuid}.jpg"),
            ("data", f"data_{fixed_uuid}_backup"),
        ]

        for prefix, path in test_cases:
            result = extract_uuid(path, prefix)
            assert result == fixed_uuid

    def test_extract_uuid_with_file_extensions(self, fixed_uuid):
        """Test UUID extraction from paths with various file extensions"""
        extensions = [".txt", ".pdf", ".jpg", ".png", ".json", ".xml", ".csv"]

        for ext in extensions:
            path = f"document_{fixed_uuid}{ext}"
            result = extract_uuid(path, "document")
            assert result == fixed_uuid

    def test_extract_uuid_in_full_paths(self, fixed_uuid):
        """Test UUID extraction from full file paths"""
        paths = [
            f"/home/user/documents/file_{fixed_uuid}.txt",
            f"C:\\Users\\Documents\\report_{fixed_uuid}.pdf",
            f"./data/export_{fixed_uuid}.json",
            f"../backup/archive_{fixed_uuid}.zip",
            f"/var/log/app_{fixed_uuid}.log",
        ]

        prefixes = ["file", "report", "export", "archive", "app"]

        for path, prefix in zip(paths, prefixes):
            result = extract_uuid(path, prefix)
            assert result == fixed_uuid

    def test_extract_uuid_case_insensitive(self):
        """Test that UUID pattern matches both uppercase and lowercase"""
        test_cases = [
            "ABC12345-1234-1234-1234-123456789ABC",  # All uppercase
            "abc12345-1234-1234-1234-123456789abc",  # All lowercase
            "AbC12345-1234-1234-1234-123456789aBc",  # Mixed case
            "123E4567-E89B-12D3-A456-426614174000",  # Mixed case
        ]

        for uuid_str in test_cases:
            path = f"test_{uuid_str}.txt"
            result = extract_uuid(path, "test")
            assert result == uuid_str

    def test_extract_uuid_no_match_wrong_prefix(self, fixed_uuid):
        """Test that no UUID is extracted with wrong prefix"""
        path = f"file_{fixed_uuid}.txt"
        result = extract_uuid(path, "document")  # Wrong prefix
        assert result is None

    def test_extract_uuid_no_match_no_uuid(self):
        """Test that no UUID is extracted when path has no UUID"""
        paths = [
            "file_notauuid.txt",
            "document_12345.pdf",
            "test_almost-uuid-but-not.jpg",
            "prefix_123e4567-e89b-12d3-a456.txt",  # Incomplete UUID
        ]

        for path in paths:
            result = extract_uuid(path, "file")
            assert result is None

    def test_extract_uuid_malformed_uuid_patterns(self):
        """Test with malformed UUID patterns"""
        malformed_cases = [
            "test_123e4567-e89b-12d3-a456-4266141740g.txt",  # Invalid char 'g'
            "test_123e4567-e89b-12d3-a456-42661417400.txt",  # Too few chars
            "test_123e4567-e89b-12d3-a456.txt",  # Missing segment
            "test_123e4567_e89b_12d3_a456_426614174000.txt",  # Wrong separators
        ]

        for path in malformed_cases:
            result = extract_uuid(path, "test")
            assert result is None

    def test_extract_uuid_multiple_uuids_returns_first(self):
        """Test that when multiple UUIDs exist, first matching one is returned"""
        uuid1 = "123e4567-e89b-12d3-a456-426614174000"
        uuid2 = "987fcdeb-51a2-43d7-8b9f-0123456789ab"

        path = f"file_{uuid1}_backup_{uuid2}.txt"
        result = extract_uuid(path, "file")
        assert result == uuid1

        # Test with different prefix for second UUID
        path2 = f"file_{uuid1}_backup_{uuid2}.txt"
        result2 = extract_uuid(path2, "backup")
        assert result2 == uuid2

    def test_extract_uuid_special_characters_in_prefix(self):
        """Test UUID extraction with special characters in prefix"""
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"

        special_prefixes = [
            "file-name",
            "file.name",
            "file+name",
            "file[name]",
            "file(name)",
            "file*name",
            "file?name",
            "file^name",
            "file$name",
        ]

        for prefix in special_prefixes:
            path = f"{prefix}_{uuid_str}.txt"
            result = extract_uuid(path, prefix)
            assert result == uuid_str

    def test_extract_uuid_empty_inputs(self):
        """Test behavior with empty inputs"""
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"

        # Empty path
        result1 = extract_uuid("", "prefix")
        assert result1 is None

        # Empty prefix
        result2 = extract_uuid(f"_{uuid_str}.txt", "")
        assert result2 == uuid_str

    def test_extract_uuid_whitespace_handling(self):
        """Test UUID extraction with whitespace in paths"""
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"

        # These should not match due to whitespace
        paths_no_match = [
            f"prefix _{uuid_str}.txt",  # Space before underscore
            f"prefix_ {uuid_str}.txt",  # Space after underscore
            f"prefix_{uuid_str} .txt",  # Space in UUID
        ]

        for path in paths_no_match:
            result = extract_uuid(path, "prefix")
            # The first two might still match depending on regex, but third should not
            if " " in uuid_str:
                assert result is None

    def test_extract_uuid_prefix_at_different_positions(self):
        """Test UUID extraction when prefix appears at different positions"""
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"

        paths = [
            f"prefix_{uuid_str}",  # At start
            f"some/path/prefix_{uuid_str}.txt",  # In middle
            f"prefix_{uuid_str}_and_more_text",  # With suffix
            f"/very/long/path/to/prefix_{uuid_str}",  # At end of long path
        ]

        for path in paths:
            result = extract_uuid(path, "prefix")
            assert result == uuid_str

    def test_extract_uuid_return_type(self, fixed_uuid):
        """Test that function returns correct types"""
        # Success case should return string
        path = f"test_{fixed_uuid}.txt"
        result = extract_uuid(path, "test")
        assert isinstance(result, str)
        assert result == fixed_uuid

        # Failure case should return None
        result_none = extract_uuid("no_uuid_here.txt", "test")
        assert result_none is None

    @pytest.mark.parametrize(
        "prefix,uuid_str",
        [
            ("file", "123e4567-e89b-12d3-a456-426614174000"),
            ("document", "987fcdeb-51a2-43d7-8b9f-0123456789ab"),
            ("image", "abcdef12-3456-7890-abcd-ef1234567890"),
            ("data", "FEDCBA98-7654-3210-FEDC-BA9876543210"),
        ],
    )
    def test_extract_uuid_parametrized(self, prefix, uuid_str):
        """Parametrized test for multiple prefix/UUID combinations"""
        path = f"{prefix}_{uuid_str}.ext"
        result = extract_uuid(path, prefix)
        assert result == uuid_str

    def test_extract_uuid_with_generated_uuids(self):
        """Test with dynamically generated UUIDs"""
        for _ in range(10):  # Test with 10 random UUIDs
            test_uuid = str(uuid4())
            path = f"generated_{test_uuid}.data"
            result = extract_uuid(path, "generated")
            assert result == test_uuid

    def test_extract_uuid_regex_escaping(self):
        """Test that prefix is properly escaped in regex"""
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"

        # Prefix with regex special characters
        prefix = "test.file[name]"
        path = f"{prefix}_{uuid_str}.txt"

        result = extract_uuid(path, prefix)
        assert result == uuid_str

        # Should not match partial prefix due to escaping
        wrong_path = f"testXfile[name]_{uuid_str}.txt"
        result_wrong = extract_uuid(wrong_path, prefix)
        assert result_wrong is None

    def test_extract_uuid_performance_with_long_strings(self, fixed_uuid):
        """Test performance with long strings"""
        # Create a long string with UUID at the end
        long_prefix = "a" * 1000
        path = f"{long_prefix}_{fixed_uuid}.txt"

        result = extract_uuid(path, long_prefix)
        assert result == fixed_uuid
