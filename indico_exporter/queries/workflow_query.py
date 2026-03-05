from indico_exporter.client.indico_client import IndicoAPIClient

WORKFLOW_QUERY = """
query Workflow($id: Int!) {
  workflow(id: $id) {
    components {
      ... on ModelGroupComponent {
        modelGroup {
          fieldLinks {
            targetId
            targetName
          }
          models {
            modelOptions
            updatedAt
          }
        }
        name
      }
    }
  }
}
"""


def fetch_workflow(workflow_id: int):
    client = IndicoAPIClient()

    variables = {"id": workflow_id}

    return client.query(WORKFLOW_QUERY, variables)
