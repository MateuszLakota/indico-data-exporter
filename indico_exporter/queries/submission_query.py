from indico_exporter.client.indico_client import IndicoAPIClient

SUBMISSION_QUERY = """
query Submission($id: Int!) {
  submission(id: $id) {
    createdAt
    inputFilename
    outputFiles {
      filepath
    }
  }
}
"""


def fetch_submission(submission_id: int):
    client = IndicoAPIClient()

    variables = {"id": submission_id}

    return client.query(SUBMISSION_QUERY, variables)
