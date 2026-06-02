import boto3

from src.settings import settings


class S3Client:
    def __init__(self):
        params = {"endpoint_url": settings.aws_s3_endpoint}

        if aws_access_key_id := settings.aws_access_key:
            params["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key := settings.aws_secret_key:
            params["aws_secret_access_key"] = aws_secret_access_key
        if region_name := settings.aws_region:
            params["region_name"] = region_name

        self.client = boto3.client("s3", **params)


s3_client = S3Client().client
