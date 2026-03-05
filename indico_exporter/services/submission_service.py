import logging

from indico_exporter.queries.submission_query import fetch_submission
from indico_exporter.serializers.submission_serializer import build_submission_rows

logger = logging.getLogger(__name__)


def export_submissions(submission_ids: list[int]):
    for submission_id in submission_ids:
        try:

            logger.info("Processing submission %s", submission_id)

            submission_body = fetch_submission(submission_id)

            build_submission_rows(submission_body, submission_id)

        except Exception as e:

            logger.error(
                "Failed to export submission %s: %s",
                submission_id,
                e
            )
