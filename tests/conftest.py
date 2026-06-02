from unittest.mock import Mock, patch

# Patch the boto3.client constructor globally
boto3_client_patch = patch("boto3.client", return_value=Mock())
boto3_client_patch.start()
