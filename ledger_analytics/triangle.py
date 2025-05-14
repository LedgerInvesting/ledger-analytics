from __future__ import annotations

import logging
from typing import Optional

from bermuda import Triangle as BermudaTriangle
from requests import Response
from requests.exceptions import ChunkedEncodingError

from .config import JSONDict
from .console import RichConsole
from .interface import TriangleInterface
from .requester import Requester

logger = logging.getLogger(__name__)


class Triangle(TriangleInterface):
    def __init__(
        self,
        id: str,
        name: str,
        data: JSONDict,
        endpoint: str,
        requester: Requester,
    ) -> None:
        self.endpoint = endpoint
        self._requester = requester
        self._id: str = id
        self._name: str = name
        self._data: JSONDict = data
        self._get_response: Response | None = None
        self._delete_response: Response | None = None
        self._captured_stdout: str = ""

    id = property(lambda self: self._id)
    name = property(lambda self: self._name)
    data = property(lambda self: self._data)
    get_response = property(lambda self: self._get_response)
    delete_response = property(lambda self: self._delete_response)
    captured_stdout = property(lambda self: self._captured_stdout)

    def to_bermuda(self):
        return BermudaTriangle.from_dict(self.data)

    @classmethod
    def get(cls, id: str, name: str, endpoint: str, requester: Requester) -> Triangle:
        console = RichConsole()
        with console.status("Retrieving...", spinner="bouncingBar") as _:
            console.log(f"Getting triangle '{name}' with ID '{id}'")
            get_response = None
            retries = 0
            max_retries = 5
            stream = False
            while get_response is None and retries < max_retries:
                try:
                    retries += 1
                    get_response = requester.get(endpoint, stream=stream)
                except ChunkedEncodingError:
                    stream = True
                    continue

        self = cls(
            id,
            name,
            get_response.json().get("triangle_data"),
            endpoint,
            requester,
        )
        self._get_response = get_response
        self._captured_stdout += console.get_stdout()
        return self

    def delete(self) -> Triangle:
        self._delete_response = self._requester.delete(self.endpoint)
        return self
