import sentry_sdk
from pydantic_settings import BaseSettings
from sentry_sdk.integrations.celery import CeleryIntegration


class Settings(BaseSettings):
    name: str = "Eunomia"
    description: str = "Core service that orchestrates the normalization of raw data"
    environment: str = "local"

    aws_access_key: str = ""
    aws_secret_key: str = ""
    aws_region: str = ""

    aws_s3_endpoint: str = ""
    aws_s3_output_bucket: str = "nova-normalized-documents-bucket"
    aws_s3_input_bucket: str = "nova-raw-documents-bucket"

    celery_broker_url: str = ""
    celery_task_queue: str = "eunomia"

    external_url: str = ""

    sentry_dsn: str = ""
    sentry_tsr: float = 1.0


settings = Settings()


def init_sentry() -> None:
    if not settings.sentry_dsn:
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=settings.sentry_tsr,
        integrations=[CeleryIntegration()],
    )
