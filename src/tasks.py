import json
import logging
import tempfile
import traceback

from src.celery import celery
from src.clients.external import notify_raw_documents_analyzed
from src.clients.s3 import s3_client
from src.models.validators import default
from src.parsers import get_file_parser
from src.settings import settings

logger = logging.getLogger(__name__)


@celery.task
def process_s3_raw_documents(input_file: str, output_folder: str, silent: bool):
    logger.info(f"Parsing file: {input_file}")
    try:
        parser = get_file_parser(input_file)

        with (
            tempfile.TemporaryFile("w+b") as raw_file,
            tempfile.TemporaryFile("w+b") as posts_file,
            tempfile.TemporaryFile("w+b") as interactions_file,
        ):
            s3_client.download_fileobj(
                settings.aws_s3_input_bucket,
                input_file,
                raw_file,
            )
            raw_file.seek(0)

            skipped_posts = 0
            skipped_interactions = 0
            for line in raw_file:
                raw_doc: dict = json.loads(line)

                try:
                    post = parser.normalize_raw_document(raw_doc)
                except KeyError:
                    post_id = raw_doc.get("id", "unknown")
                    logger.info(f"KeyError in post with ID {post_id}. Skipping...")
                    skipped_posts += 1
                    continue
                if not post:
                    continue
                post_line = json.dumps(post, default=default) + "\n"
                posts_file.write(post_line.encode("utf-8"))

                try:
                    interactions = parser.get_document_interactions(raw_doc)
                except KeyError:
                    post_id = raw_doc.get("id", "unknown")
                    logger.info(f"KeyError in post with ID {post_id}. Skipping...")
                    skipped_interactions += 1
                    continue
                if not interactions:
                    continue
                for interaction in interactions:
                    interaction_line = json.dumps(interaction, default=default) + "\n"
                    interactions_file.write(interaction_line.encode("utf_8"))

            written_files = []
            posts_file.seek(0)
            output_path = f"{output_folder}/posts.jsonl"
            s3_client.upload_fileobj(
                posts_file,
                settings.aws_s3_output_bucket,
                output_path,
            )
            written_files.append(output_path)

            interactions_file.seek(0)
            output_path = f"{output_folder}/interactions.jsonl"
            s3_client.upload_fileobj(
                interactions_file,
                settings.aws_s3_output_bucket,
                output_path,
            )
            written_files.append(output_path)

        if not silent:
            notify_raw_documents_analyzed(input_file, files=written_files)

        logger.info(f"Skipped {skipped_posts} posts")
        logger.info(f"Skipped {skipped_interactions} interactions")
    except Exception as e:
        if not silent:
            notify_raw_documents_analyzed(input_file, status="error", detail=str(e))
        logger.error(traceback.format_exc())
