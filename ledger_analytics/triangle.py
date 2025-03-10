from __future__ import annotations

from typing import Any

import requests
from bermuda import Triangle


class TriangleResponse(object):
    ENDPOINT = "triangle"

    def __init__(self, host: str, headers: dict[str, str] | None = None) -> None:
        self.host = host
        self.headers = headers
        self._triangle_id: str | None = None

    triangle_id = property(lambda self: self._triangle_id)

    def create(self, config: dict[str, Any]) -> TriangleResponse:
        response = requests.post(
            self.host + self.ENDPOINT, json=config, headers=self.headers
        )
        status = response.status_code
        if status != 201:
            raise requests.HTTPError(
                f"Post request to {self.host + self.ENDPOINT} raised {status} error with details: {response.json()}"
            )
        self._triangle_id = response.json().get("id")
        return self

    def get(self, triangle_id: str | None = None) -> Triangle:
        if triangle_id is None and self.triangle_id is None:
            raise ValueError("Must pass a `triangle_id` to get request")

        if triangle_id is None:
            triangle_id = self.triangle_id

        response = requests.get(
            self.host + self.ENDPOINT + "/" + triangle_id, headers=self.headers
        )
        status = response.status_code
        if status != 200:
            raise requests.HTTPError(
                f"Get request to {self.host + self.ENDPOINT} raised {status} error with details: {response.json()}"
            )
        triangle_json = response.json().get("triangle_data")
        return Triangle.from_dict(triangle_json)

    def delete(self, triangle_id: str | None = None) -> TriangleResponse:
        if triangle_id is None and self.triangle_id is None:
            raise ValueError("Must pass a `triangle_id` to delete request")

        if triangle_id is None:
            triangle_id = self.triangle_id

        response = requests.delete(
            self.host + self.ENDPOINT + "/" + triangle_id, headers=self.headers
        )
        status = response.status_code
        if status != 204:
            raise requests.HTTPError(
                f"Get request to {self.host + self.ENDPOINT} raised {status} error with details: {response.json()}"
            )
