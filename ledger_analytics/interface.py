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
        host: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        self.endpoint = host + "triangle"
        self._requester = requester
        self.asynchronous = asynchronous

    def create(self, triangle_name: str, triangle_data: ConfigDict):
        if isinstance(triangle_data, BermudaTriangle):
            triangle_data = triangle_data.to_dict()

        config = {
            "triangle_name": triangle_name,
            "triangle_data": triangle_data,
        }

        post_response = self._requester.post(self.endpoint, data=config)
        triangle_id = post_response.json().get("id")
        logger.info(f"Created triangle '{triangle_name}' with ID {triangle_id}.")

        endpoint = self.endpoint + f"/{triangle_id}"
        triangle = TriangleRegistry.REGISTRY["triangle"](
            triangle_id,
            triangle_name,
            triangle_data,
            endpoint,
            self._requester,
        )
        triangle._post_response = post_response
        return triangle

    def get(self, triangle_name: str | None = None, triangle_id: str | None = None):
        triangle_obj = self._get_details_from_id_name(triangle_name, triangle_id)
        return TriangleRegistry.REGISTRY["triangle"].get(
            triangle_obj["id"],
            triangle_obj["name"],
            self.endpoint + f"/{triangle_obj['id']}",
            self._requester,
        )

    def delete(
        self, triangle_name: str | None = None, triangle_id: str | None = None
    ) -> None:
        triangle = self.get(triangle_name, triangle_id)
        triangle.delete()

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
        model_class: str,
        host: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        self._model_class = model_class
        self._endpoint = host + self.model_class_slug
        self._requester = requester
        self._asynchronous = asynchronous

    model_class = property(lambda self: self._model_class)
    endpoint = property(lambda self: self._endpoint)

    def create(
        self,
        triangle_name: str,
        model_name: str,
        model_type: str,
        model_config: ConfigDict | None = None,
    ):
        return ModelRegistry.REGISTRY[self.model_class].fit_from_interface(
            triangle_name,
            model_name,
            model_type,
            model_config,
            self.model_class,
            self.endpoint,
            self._requester,
            self._asynchronous,
        )

    def get(self, model_name: str | None = None, model_id: str | None = None):
        model_obj = self._get_details_from_id_name(model_name, model_id)
        endpoint = self.endpoint + f"/{model_obj['id']}"
        return ModelRegistry.REGISTRY[self.model_class].get(
            model_obj["id"],
            model_obj["name"],
            model_obj["modal_task_info"]["task_args"]["model_type"],
            model_obj["modal_task_info"]["task_args"]["model_config"],
            self.model_class,
            endpoint,
            self._requester,
            self._asynchronous,
        )

    def predict(
        self,
        triangle_name: str,
        model_name: str | None = None,
        model_id: str | None = None,
    ):
        model = self.get(model_name, model_id)
        return model.predict(triangle_name)

    def delete(
        self, model_name: str | None = None, model_id: str | None = None
    ) -> None:
        model = self.get(model_name, model_id)
        model.delete()
        return None

    def list(self) -> list[ConfigDict]:
        return self._requester.get(self.endpoint).json()

    def list_model_types(self) -> list[ConfigDict]:
        url = self.endpoint + "-type"
        return self._requester.get(url).json()

    @property
    def model_class_slug(self):
        return self.model_class.replace("_", "-")

    def _get_details_from_id_name(
        self, model_name: str | None = None, model_id: str | None = None
    ) -> str:
        models = [
            result
            for result in self.list().get("results")
            if result.get("name") == model_name or result.get("id") == model_id
        ]
        if not len(models):
            name_or_id = (
                f"name '{model_name}'" if model_id is None else f"ID '{model_id}'"
            )
            raise ValueError(f"No model found with {name_or_id}.")
        return models[0]
