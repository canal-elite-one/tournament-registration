import json

from fastapi.openapi.utils import get_openapi

from apis.public import app


if __name__ == "__main__":
    openapi_schema = get_openapi(
        title="USKB Tournament",
        version="3.0.0",
        summary="OpenAPI schema for USKB Tournament API",
        routes=app.routes,
        servers=[
            {"url": "http://localhost:8000", "description": "Local development server"},
        ],
    )
    print(json.dumps(openapi_schema, indent=2))  # noqa: T201
