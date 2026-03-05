from indico import IndicoClient, IndicoConfig
from indico.client.request import GraphQLRequest

from indico_exporter.config.settings import load_settings


class IndicoAPIClient:

    def __init__(self):

        settings = load_settings()

        config = IndicoConfig(
            host=settings.api_url,
            api_token=settings.api_token
        )

        self.client = IndicoClient(config)

    def query(self, query: str, variables: dict):

        request = GraphQLRequest(
            query=query,
            variables=variables
        )

        return self.client.call(request)