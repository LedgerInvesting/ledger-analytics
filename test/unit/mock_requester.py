import requests
from bermuda import meyers_tri
from requests_mock import Mocker

from ledger_analytics import Requester
from ledger_analytics.types import ConfigDict, HTTPMethods


class TriangleMockRequester(Requester):
    def _factory(self, method: HTTPMethods, url: str, data: ConfigDict):
        with Mocker() as mocker:
            if method.lower() == "post":
                mocker.post(url, json={"id": "abc"}, status_code=201)
                response = requests.post(url)
            elif method.lower() == "get":
                mocker.get(
                    url,
                    json={
                        "triangle_name": "test_meyers_triangle",
                        "triangle_data": meyers_tri.to_dict(),
                    },
                    status_code=200,
                )
                response = requests.get(url)
            elif method.lower() == "delete":
                mocker.delete(url, status_code=201)
                response = requests.delete(url)
            else:
                raise ValueError(f"Unrecognized HTTPMethod {method}.")

        self._catch_status(response)
        return response


class TriangleMockRequesterAfterDeletion(Requester):
    def _factory(self, method: HTTPMethods, url: str, data: ConfigDict):
        with Mocker() as mocker:
            if method.lower() == "post":
                mocker.post(url, json={"id": "abc"}, status_code=201)
                response = requests.post(url)
            elif method.lower() == "get":
                mocker.get(url, status_code=404)
                response = requests.get(url)
            elif method.lower() == "delete":
                mocker.delete(url, status_code=201)
                response = requests.delete(url)
            else:
                raise ValueError(f"Unrecognized HTTPMethod {method}.")

        self._catch_status(response)
        return response
