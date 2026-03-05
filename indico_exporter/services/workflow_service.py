import logging

from indico_exporter.queries.workflow_query import fetch_workflow
from indico_exporter.serializers.workflow_serializer import serialize_workflow_to_csv

logger = logging.getLogger(__name__)


def export_workflow(workflow_id: int):
    logger.info("Fetching workflow %s", workflow_id)

    workflow_body = fetch_workflow(workflow_id)

    serialize_workflow_to_csv(workflow_body, workflow_id)

    logger.info("Workflow export complete")
