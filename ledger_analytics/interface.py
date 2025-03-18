from __future__ import annotations

from abc import ABC

from .requester import Requester
from .types import ConfigDict


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
    # TODO: Make a generic Interface class and subclass it for TriangleInterface/ModelInterface?

    def __init__(
        self,
        triangle_type: str,
        host: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        self.triangle_type = triangle_type  # probably not needed
        self.endpoint = host + "triangle"
        self._requester = requester
        self.asynchronous = asynchronous

    def create(self, triangle_name, triangle_data):
        # TODO: what should this return? A ledger_analytics.Triangle?
        triangle = TriangleRegistry.REGISTRY[self.triangle_type](
            self.endpoint, self._requester, self.asynchronous
        )
        return triangle.create(triangle_name, triangle_data)

    def get(self, triangle_name: str | None = None, triangle_id: str | None = None):
        return [
            result
            for result in self.list().get("results")
            if result.get("name") == triangle_name or result.get("id") == triangle_id
        ]

    def delete(self, triangle_id: str) -> None:
        self._requester.delete(self.endpoint + f"/{triangle_id}")
        return None

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

    def create(self):
        # Should this call a LedgerModel.create method, with a model_name attribute?
        # Then, LedgerModel.fit doesn't need to take a model_name
        return ModelRegistry.REGISTRY[self.model_type](
            self.endpoint, self._requester, self.asynchronous
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
