from __future__ import annotations

from dataclasses import dataclass

from bermuda import Triangle as BermudaTriangle
from requests import HTTPError, Response

from .requester import Requester
from .types import ConfigDict


class Triangles(object):
    BASE_ENDPOINT = "triangle"

    def __init__(
        self,
        host: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        self.endpoint = host + self.BASE_ENDPOINT
        self._requester = requester
        self.asynchronous = asynchronous

    def create(
        self,
        triangle_name: str,
        triangle_data: ConfigDict | BermudaTriangle | None = None,
    ) -> Response:
        if isinstance(triangle_data, BermudaTriangle):
            triangle_data = triangle_data.to_dict()

        config = {
            "triangle_name": triangle_name,
            "triangle_data": triangle_data,
        }

        post_response = self._requester.post(self.endpoint, data=config)
        return post_response

    def get(
        self, triangle_id: str | None = None, triangle_name: str | None = None
    ) -> BermudaTriangle:
        if triangle_id is None and triangle_name is None:
            raise ValueError(
                "Must create a triangle object first or pass an existing `triangle_name` or `triangle_id` to the get request."
            )

        elif triangle_id is None:
            triangle_ids = {
                result["name"]: result["id"] for result in self.list()["results"]
            }
            triangle_id = triangle_ids[triangle_name]

        get_response = self._requester.get(self.endpoint + f"/{triangle_id}")

        return Triangle.from_response(get_response)

    def delete(
        self, triangle: Triangle | None, triangle_id: str | None = None
    ) -> Response:
        if triangle_id is None and triangle is None:
            raise ValueError(
                "Must pass a `triangle` or `triangle_id` to delete request"
            )

        if triangle_id is None:
            triangle_id = triangle.triangle_id

        delete_response = self._requester.delete(self.endpoint + f"/{triangle_id}")
        return delete_response

    def list(self) -> list[ConfigDict]:
        return self._requester.get(self.endpoint).json()


@dataclass
class Triangle:
    triangle_id: str
    triangle_name: str
    response: Response

    @classmethod
    def from_response(cls, response: Response) -> Triangle:
        triangle_json = response.json()
        triangle_id = triangle_json.get("id")
        triangle_name = triangle_json.get("triangle_name")
        return cls(triangle_id, triangle_name, response)

    def to_bermuda(self) -> BermudaTriangle:
        try:
            triangle_json = self.response.json().get("triangle_data")
        except Exception:
            raise HTTPError(
                f"Cannot get valid triangle data from response: {self.response}"
            )

        if triangle_json is None:
            raise HTTPError(
                f"Cannot get valid triangle data from response: {self.response}"
            )
        return BermudaTriangle.from_dict(triangle_json)
