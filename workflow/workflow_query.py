WORKFLOW_QUERY = """
query GetWorkflow($id: Int!) {
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
