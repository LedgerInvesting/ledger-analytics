from __future__ import annotations

from bermuda import Triangle as BermudaTriangle
from requests import HTTPError, Response

from .requester import Requester
from .types import JSONData


class Triangle(object):
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
        self._triangle_id: str | None = None
        self._post_response: Response | None = None
        self._get_response: Response | None = None
        self._delete_response: Response | None = None

    triangle_id = property(lambda self: self._triangle_id)
    get_response = property(lambda self: self._get_response)
    post_response = property(lambda self: self._post_response)
    delete_response = property(lambda self: self._delete_response)

    def create(self, config: JSONData) -> Triangle:
        self._post_response = self._requester.post(self.endpoint, data=config)

        try:
            self._triangle_id = self._post_response.json().get("id")
        except Exception:
            raise HTTPError(
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

        self._get_response = self._requester.get(self.endpoint + f"/{triangle_id}")

        try:
            triangle_json = self._get_response.json().get("triangle_data")
        except Exception:
            raise HTTPError(
                f"Cannot get valid triangle data from response: {self._get_response}"
            )

        if triangle_json is None:
            raise HTTPError(
                f"Cannot get valid triangle data from response: {self._get_response}"
            )

        return BermudaTriangle.from_dict(triangle_json)

    def delete(self, triangle_id: str | None = None) -> Triangle:
        if triangle_id is None and self.triangle_id is None:
            raise ValueError("Must pass a `triangle_id` to delete request")

        if triangle_id is None:
            triangle_id = self.triangle_id

        self._delete_response = self._requester.delete(
            self.endpoint + f"/{triangle_id}"
        )
        return self

    def list(self) -> list[JSONData]:
        return self._requester.get(self.host + self.BASE_ENDPOINT)
