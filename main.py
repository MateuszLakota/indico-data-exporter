from indico import IndicoClient, IndicoConfig
from indico.client.request import GraphQLRequest

from workflow.csv_workflow_serializer import serialize_workflow_to_csv
from workflow.workflow_query import WORKFLOW_QUERY

ALLIANZ_API_TOKEN = ""
ALLIANZ_URL = ""

AVIVA_API_TOKEN = ""
AVIVA_URL = ""

BATCH_SIZE = 10  # tweak between 3–20 safely
WORKFLOW_ID = 2
SUBMISSIONS_ID = [139, 140, 141, 145, 148, 150, 151, 152]


def serialize_workflow_response_to_csv(workflow_id: int):
    config = IndicoConfig(host=AVIVA_URL, api_token=AVIVA_API_TOKEN)
    client = IndicoClient(config)

    response = client.call(
        GraphQLRequest(query=WORKFLOW_QUERY, variables={"id": workflow_id})
    )

    serialize_workflow_to_csv(response, workflow_id)


if __name__ == "__main__":
    serialize_workflow_response_to_csv(WORKFLOW_ID)
