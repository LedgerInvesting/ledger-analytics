from __future__ import annotations

import logging

from bermuda import Triangle as BermudaTriangle
from requests import HTTPError, Response

from .interface import TriangleInterface
from .requester import Requester
from .types import ConfigDict

logger = logging.getLogger(__name__)


class Triangle(TriangleInterface):
    def __init__(
        self,
        triangle_id: str,
        triangle_name: str,
        triangle_data: ConfigDict,
        endpoint: str,
        requester: Requester,
    ) -> None:
        self.endpoint = endpoint
        self._requester = requester
        self._triangle_id: str = triangle_id
        self._triangle_name: str = triangle_name
        self._triangle_data: ConfigDict = triangle_data
        self._get_response: Response | None = None
        self._delete_response: Response | None = None

    triangle_id = property(lambda self: self._triangle_id)
    triangle_name = property(lambda self: self._triangle_name)
    triangle_data = property(lambda self: self._triangle_data)
    get_response = property(lambda self: self._get_response)
    delete_response = property(lambda self: self._delete_response)

    def to_bermuda(self):
        return BermudaTriangle.from_dict(self.triangle_data)

    def get(self) -> Triangle:
        self._get_response = self._requester.get(self.endpoint)
        return self

    def delete(self) -> Triangle:
        self._delete_response = self._requester.delete(self.endpoint)
        return self
