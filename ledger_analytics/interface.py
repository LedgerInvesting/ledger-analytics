from __future__ import annotations

import logging
from abc import ABC

from bermuda import Triangle as BermudaTriangle
from requests import Response

from .requester import Requester
from .types import ConfigDict

logger = logging.getLogger(__name__)


def to_snake_case(x: str) -> str:
    uppers = [s.isupper() if i > 0 else False for i, s in enumerate(x)]
    snake = ["_" + s.lower() if upper else s for upper, s in zip(uppers, x.lower())]
    return "".join(snake)


class Registry(type):
    REGISTRY = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.REGISTRY[to_snake_case(new_cls.__name__)] = new_cls
        return new_cls


class TriangleRegistry(Registry):
    pass


class ModelRegistry(Registry):
    pass


class TriangleInterface(metaclass=TriangleRegistry):
    """The TriangleInterface class handles the basic CRUD operations
    on triangles, managed through AnalyticsClient.
    """

    def __init__(
        self,
        triangle_type: str,
        host: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        self.triangle_type = triangle_type
        self.endpoint = host + "triangle"
        self._requester = requester
        self.asynchronous = asynchronous
        self._post_response: Response | None = None
        self._get_response: Response | None = None
        self._delete_response: Response | None = None

    get_response = property(lambda self: self._get_response)
    post_response = property(lambda self: self._post_response)
    delete_response = property(lambda self: self._delete_response)

    def create(self, triangle_name: str, triangle_data: ConfigDict):
        if isinstance(triangle_data, BermudaTriangle):
            triangle_data = triangle_data.to_dict()

        config = {
            "triangle_name": triangle_name,
            "triangle_data": triangle_data,
        }

        self._post_response = self._requester.post(self.endpoint, data=config)
        triangle_id = self._post_response.json().get("id")
        logger.info(f"Created triangle '{triangle_name}' with ID {triangle_id}.")

        endpoint = self.endpoint + f"/{triangle_id}"
        triangle = TriangleRegistry.REGISTRY[self.triangle_type](
            triangle_id,
            triangle_name,
            triangle_data,
            endpoint,
            self._requester,
        )
        return triangle

    def get(self, triangle_name: str | None = None, triangle_id: str | None = None):
        triangle_obj = self._get_details_from_id_name(triangle_name, triangle_id)
        self._get_response = self._requester.get(
            self.endpoint + f"/{triangle_obj['id']}"
        )
        triangle = TriangleRegistry.REGISTRY[self.triangle_type](
            triangle_obj["id"],
            triangle_obj["name"],
            self.get_response.json().get("triangle_data"),
            self.endpoint + f"/{triangle_id}",
            self._requester,
        )
        return triangle

    def delete(
        self, triangle_name: str | None = None, triangle_id: str | None = None
    ) -> None:
        triangle_obj = self._get_details_from_id_name(triangle_name, triangle_id)
        self._requester.delete(self.endpoint + f"/{triangle_obj['id']}")
        logger.info(
            f"Deleted triangle '{triangle_obj['name']}' (id: {triangle_obj['id']})."
        )
        return None

    def _get_details_from_id_name(
        self, triangle_name: str | None = None, triangle_id: str | None = None
    ) -> str:
        triangles = [
            result
            for result in self.list().get("results")
            if result.get("name") == triangle_name or result.get("id") == triangle_id
        ]
        if not len(triangles):
            name_or_id = (
                f"name '{triangle_name}'"
                if triangle_id is None
                else f"ID '{triangle_id}'"
            )
            raise ValueError(f"No triangle found with {name_or_id}.")
        return triangles[0]

    def list(self) -> list[ConfigDict]:
        return self._requester.get(self.endpoint).json()


class ModelInterface(metaclass=ModelRegistry):
    def __init__(
        self,
        model_type: str,
        host: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        self.model_type = model_type
        self.endpoint = host
        self._requester = requester
        self.asynchronous = asynchronous

    def create(
        self,
        triangle_name: str,
        model_name: str,
        model_type: str,
        model_config: ConfigDict | None = None,
    ):
        return ModelRegistry.REGISTRY[self.model_type].fit_from_interface(
            triangle_name,
            model_name,
            model_type,
            model_config,
            self.endpoint,
            self._requester,
            self.asynchronous,
        )

    def get(self, model_id: str):
        # Not implemented yet really, not sure it's needed.
        model = ModelRegistry[self.model_type](
            self.endpoint, self._requester, self.asynchronous
        )
        return model.get(model_id)

    def list(self) -> list[ConfigDict]:
        return self._requester.get(self.endpoint + self.slug).json()

    def list_model_types(self) -> list[ConfigDict]:
        url = self.endpoint + self.slug + "-type"
        return self._requester.get(url).json()

    @property
    def slug(self):
        return self.model_type.replace("_", "-")
