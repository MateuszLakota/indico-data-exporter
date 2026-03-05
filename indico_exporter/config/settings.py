import os
from dataclasses import dataclass


@dataclass
class Settings:
    api_url: str
    api_token: str
    timeout: int


def load_settings() -> Settings:
    return Settings(
        api_url="aviva-dev.ca-central-1.aviva-ca.indico.io",#os.getenv("INDICO_API_URL"),
        api_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjUyLCJ1c2VyX2lkIjo4OSwidXNlcl9lbWFpbCI6Im1hdGV1c3oubGFrb3RhQHNvbGxlcnMuZXUiLCJpYXQiOjE3NzI3MjA1NTYsImF1ZCI6WyJpbmRpY286cmVmcmVzaF90b2tlbiJdfQ.KIta-HTtr8lngZRtCyM7XG-w6oaY1VWO97RG_IH06d8",#os.getenv("INDICO_API_TOKEN"),
        timeout=30#int(os.getenv("REQUEST_TIMEOUT", "30")),
    )
