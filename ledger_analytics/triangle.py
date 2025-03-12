from __future__ import annotations

from typing import Any

import requests
from bermuda import Triangle as BermudaTriangle


class Triangle(object):
    ENDPOINT = "triangle"

    def __init__(
        self,
        host: str,
        headers: dict[str, str] | None = None,
        asynchronous: bool = False,
    ) -> None:
        self.host = host
        self.headers = headers
        self.asynchronous = asynchronous
        self._triangle_id: str | None = None
        self._post_response: requests.Response | None = None
        self._get_response: requests.Response | None = None
        self._delete_response: requests.Response | None = None

    triangle_id = property(lambda self: self._triangle_id)
    get_response = property(lambda self: self._get_response)
    post_response = property(lambda self: self._post_response)
    delete_response = property(lambda self: self._delete_response)

    def create(self, config: dict[str, Any]) -> Triangle:
        self._post_response = requests.post(
            self.host + self.ENDPOINT, json=config, headers=self.headers
        )
        try:
            self._triangle_id = self._post_response.json().get("id")
        except Exception:
            raise requests.HTTPError(
                f"Cannot get valid triangle ID from response: {self._post_response}"
            )
        return self

    def get(self, triangle_id: str | None = None) -> BermudaTriangle:
        if triangle_id is None and self.triangle_id is None:
            raise ValueError(
                "Must create a triangle object first or pass a `triangle_id` to the get request."
            )

        if triangle_id is None:
            triangle_id = self.triangle_id

        self._get_response = requests.get(
            self.host + self.ENDPOINT + "/" + triangle_id, headers=self.headers
        )
        try:
            triangle_json = self._get_response.json().get("triangle_data")
        except Exception:
            raise requests.HTTPError(
                f"Cannot get valid triangle data from response: {self._get_response}"
            )

        if triangle_json is None:
            breakpoint()
            raise requests.HTTPError(
                f"Cannot get valid triangle data from response: {self._get_response}"
            )

        return BermudaTriangle.from_dict(triangle_json)

    def delete(self, triangle_id: str | None = None) -> Triangle:
        if triangle_id is None and self.triangle_id is None:
            raise ValueError("Must pass a `triangle_id` to delete request")

        if triangle_id is None:
            triangle_id = self.triangle_id

        self._delete_response = requests.delete(
            self.host + self.ENDPOINT + "/" + triangle_id, headers=self.headers
        )
        return self

    def list(self) -> list[dict[str, Any]]:
        return requests.get(self.host + self.ENDPOINT, headers=self.headers)
